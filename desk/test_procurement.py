import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from decimal import Decimal
from unittest import skipUnless
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.db import connection,transaction,IntegrityError,close_old_connections
from django.test import TestCase,TransactionTestCase,override_settings
from django.utils import timezone
from .test_assets import AssetFixtures
from .models import (Person,RoleGrant,Supplier,Contract,Stockroom,StockItem,StockBalance,StockMovement,
    PurchaseRequisition,PurchaseOrder,GoodsReceipt,Asset,StockAsset,AssetContractLink,AssetCustody)
from . import services as s,procurement as p

class SupplyFixtures(AssetFixtures):
    @classmethod
    def build_supply(cls):
        cls.build_inventory()
        def user(name,roles):
            u=get_user_model().objects.create_user(username=name,password='test-only-password')
            person=Person.objects.create(organization=cls.org,user=u,display_name=name)
            for role in roles: RoleGrant.objects.create(organization=cls.org,person=person,role=role)
            return person
        cls.buyer=user('buyer',['PROCUREMENT_MANAGER'])
        cls.stock=user('stock',['STOCK_MANAGER','ASSET_MANAGER','RESOURCE_READER'])
        cls.supplier=Supplier.objects.create(organization=cls.org,code='S1',name='Supplier',contact='PRIVATE-CONTACT')
        today=timezone.localdate()
        cls.contract=Contract.objects.create(organization=cls.org,supplier=cls.supplier,code='C1',name='Contract',
            starts_on=today-timedelta(days=30),ends_on=today+timedelta(days=365),currency='KRW',amount=Decimal('10000'),notes='PRIVATE-FINANCE')
        cls.room=Stockroom.objects.create(organization=cls.org,code='MAIN',name='Main warehouse',location='Seoul warehouse')
        cls.other_room=Stockroom.objects.create(organization=cls.org,code='SECOND',name='Second warehouse',location='Busan warehouse')
        cls.bulk=StockItem.objects.create(organization=cls.org,code='CABLE',name='Cable',tracking='BULK')
        cls.serial=StockItem.objects.create(organization=cls.org,code='DEVICE',name='Laptop',tracking='SERIALIZED',manufacturer='StockMaker',model='Model S')

    def call(self,actor,op,data,target=None,key=None):
        return s.execute(actor,op,data,key or uuid.uuid4().hex,uuid.uuid4(),uuid.UUID(str(target)) if target else None)[0]

    def request_purchase(self,item=None,qty=5,price='1000',unit='KRW'):
        return self.call(self.manager,'buy_request',{'item_id':str((item or self.bulk).id),'quantity':qty,'currency':unit,
            'max_unit_price':price,'approver_id':str(self.buyer.id),'reason':'IT purchase'})

    def approve(self,r):
        return self.call(self.buyer,'buy_decide',{'decision':'APPROVE','expected_version':r['version']},r['id'])

    def draft(self,r,price='1000',contract='default'):
        c=self.contract if contract=='default' else contract
        return self.call(self.buyer,'buy_order',{'requisition_id':r['id'],'supplier_id':str(self.supplier.id),
            'contract_id':str(c.id) if c else None,'unit_price':price,'expected_version':r['version']})

    def release(self,o):
        return self.call(self.buyer,'buy_order_action',{'action':'RELEASE','reason':'Place order','expected_version':o['version']},o['id'])

    def ready_order(self,item=None,qty=5,contract='default'):
        return self.release(self.draft(self.approve(self.request_purchase(item,qty)),contract=contract))

    def receive(self,o,qty,ref,serials=None,key=None):
        return self.call(self.stock,'buy_receipt',{'stockroom_id':str(self.room.id),'quantity':qty,'reference':ref,
            'serials':serials or [],'reason':'Goods arrival','expected_version':o['version']},o['id'],key)

    def fresh(self,o): return p.order_data(PurchaseOrder.objects.get(id=o['id']),self.buyer)

@override_settings(SECURE_SSL_REDIRECT=False)
class ProcurementTests(SupplyFixtures,TestCase):
    @classmethod
    def setUpTestData(cls): cls.build_supply()

    def test_purchase_approval_order_partial_receipt_and_balances(self):
        o=self.ready_order();self.receive(o,2,'DELIVERY-1')
        o=self.fresh(o);self.assertEqual(o['status'],'PART_RECEIVED');self.assertEqual(o['remaining_quantity'],3)
        self.receive(o,3,'DELIVERY-2');o=self.fresh(o)
        self.assertEqual(o['status'],'RECEIVED');self.assertEqual(StockBalance.objects.get(item=self.bulk).quantity,5)
        self.assertEqual(StockMovement.objects.filter(kind='RECEIPT').count(),2)

    def test_approval_required_and_self_approval_forbidden(self):
        r=self.request_purchase()
        with self.assertRaises(s.BusinessError): self.draft(r)
        with self.assertRaises(s.BusinessError):
            self.call(self.buyer,'buy_request',{'item_id':str(self.bulk.id),'quantity':1,'currency':'KRW',
                'max_unit_price':'10','approver_id':str(self.buyer.id),'reason':'self'})
        with self.assertRaises(s.BusinessError):
            self.call(self.manager,'buy_decide',{'decision':'APPROVE','expected_version':1},r['id'])

    def test_approved_unit_price_limit_and_exact_money(self):
        r=self.approve(self.request_purchase(price='1000'))
        with self.assertRaises(s.BusinessError): self.draft(r,price='1001')
        usd=self.approve(self.request_purchase(qty=2,price='1.25',unit='USD'))
        order=self.draft(usd,price='1.23',contract=None)
        self.assertEqual(order['total'],'2.46')
        for value in ['NaN','Infinity','1e3','-1','0','1.123',True,1.5]:
            with self.assertRaises(s.BusinessError): self.request_purchase(price=value)
        with self.assertRaises(s.BusinessError): self.request_purchase(price='1.10')

    def test_contract_currency_supplier_and_expiry(self):
        r=self.approve(self.request_purchase(unit='USD'))
        with self.assertRaises(s.BusinessError): self.draft(r)
        today=timezone.localdate()
        expired=Contract.objects.create(organization=self.org,supplier=self.supplier,code='EX',name='Expired',
            starts_on=today-timedelta(days=30),ends_on=today-timedelta(days=1),currency='KRW',amount=10000)
        o=self.draft(self.approve(self.request_purchase()),contract=expired)
        with self.assertRaises(s.BusinessError) as error: self.release(o)
        self.assertEqual(error.exception.code,'CONTRACT_EXPIRED')

    def test_contract_budget_commitment_cancellation_and_reorder(self):
        today=timezone.localdate();cap=Contract.objects.create(organization=self.org,supplier=self.supplier,code='CAP',name='Cap',
            starts_on=today,ends_on=today+timedelta(days=30),currency='KRW',amount=6000)
        first=self.ready_order(qty=5,contract=cap)
        second=self.draft(self.approve(self.request_purchase(qty=2)),contract=cap)
        with self.assertRaises(s.BusinessError): self.release(second)
        self.call(self.buyer,'buy_order_action',{'action':'CANCEL','reason':'cancel','expected_version':first['version']},first['id'])
        self.release(second)
        original=PurchaseRequisition.objects.get(id=first['requisition_id'])
        self.assertEqual(original.status,'APPROVED')
        self.assertEqual(self.draft(p.requisition_data(original,self.buyer),contract=cap)['status'],'DRAFT')

    def test_over_receipt_duplicate_reference_and_no_cancel_after_receipt(self):
        o=self.ready_order()
        with self.assertRaises(s.BusinessError): self.receive(o,6,'OVER')
        self.receive(o,2,'ONCE');o=self.fresh(o)
        with self.assertRaises(IntegrityError): self.receive(o,1,'ONCE')
        with self.assertRaises(s.BusinessError):
            self.call(self.buyer,'buy_order_action',{'action':'CANCEL','reason':'bad','expected_version':o['version']},o['id'])
        self.assertEqual(StockBalance.objects.get(item=self.bulk).quantity,2)
        self.assertEqual(GoodsReceipt.objects.count(),1)

    def test_idempotent_receipt_and_request(self):
        data={'item_id':str(self.bulk.id),'quantity':5,'currency':'KRW','max_unit_price':'1000','approver_id':str(self.buyer.id),'reason':'x'}
        a=self.call(self.manager,'buy_request',data,key='same');b=self.call(self.manager,'buy_request',data,key='same')
        self.assertEqual(a,b)
        o=self.release(self.draft(self.approve(a)))
        one=self.receive(o,2,'RETRY',key='same');two=self.receive(o,2,'RETRY',key='same')
        self.assertEqual(one,two);self.assertEqual(GoodsReceipt.objects.count(),1)

    def test_bulk_transfer_issue_and_negative_stock_prevention(self):
        o=self.ready_order();self.receive(o,5,'ALL');balance=StockBalance.objects.get(item=self.bulk,stockroom=self.room)
        transfer={'item_id':str(self.bulk.id),'source_id':str(self.room.id),'target_id':str(self.other_room.id),'quantity':2,
            'reason':'Move','expected_source_version':balance.row_version,'expected_target_version':0,'asset_ids':[],'asset_versions':{}}
        self.call(self.stock,'stock_transfer',transfer)
        balance.refresh_from_db();self.assertEqual(balance.quantity,3)
        issue={'item_id':str(self.bulk.id),'source_id':str(self.room.id),'quantity':4,'reason':'Use',
            'expected_source_version':balance.row_version,'person_id':str(self.employee.id),'destination':'Desk'}
        with self.assertRaises(s.BusinessError): self.call(self.stock,'stock_issue',issue)
        self.call(self.stock,'stock_issue',{**issue,'quantity':3})
        balance.refresh_from_db();self.assertEqual(balance.quantity,0)

    def test_serialized_receipt_creates_assets_contracts_and_stock(self):
        o=self.ready_order(self.serial,2)
        result=self.receive(o,2,'DEVICES',[{'asset_no':'S-100','serial_number':'SER-100'},{'asset_no':'S-101','serial_number':'SER-101'}])
        self.assertEqual(len(result['assets']),2);self.assertEqual(StockAsset.objects.count(),2)
        self.assertEqual(AssetContractLink.objects.count(),2)
        self.assertEqual(StockBalance.objects.get(item=self.serial).quantity,2)
        self.assertTrue(all(a.status=='STOCK' for a in Asset.objects.filter(stock_record__isnull=False)))

    def test_serialized_issue_return_transfer_retire_synchronize_balance(self):
        o=self.ready_order(self.serial,2)
        result=self.receive(o,2,'DEVICES',[{'asset_no':'S-100','serial_number':'SER-100'},{'asset_no':'S-101','serial_number':'SER-101'}])
        a=Asset.objects.get(id=result['assets'][0]['id'])
        issue={'action':'ISSUE','person_id':str(self.employee.id),'location':'Desk','reason':'Use','expected_version':a.row_version}
        self.call(self.stock,'asset_action',issue,a.id)
        self.assertEqual(StockBalance.objects.get(item=self.serial,stockroom=self.room).quantity,1)
        a.refresh_from_db();self.assertIsNone(a.stock_record.stockroom_id)
        self.call(self.stock,'asset_action',{'action':'RETURN','location':'ignored','reason':'Return','expected_version':a.row_version,
            'stockroom_id':str(self.other_room.id)},a.id)
        a.refresh_from_db();self.assertEqual(a.location,self.other_room.location)
        b=StockBalance.objects.get(item=self.serial,stockroom=self.other_room);target=StockBalance.objects.get(item=self.serial,stockroom=self.room)
        self.call(self.stock,'stock_transfer',{'item_id':str(self.serial.id),'source_id':str(self.other_room.id),
            'target_id':str(self.room.id),'quantity':1,'reason':'Transfer','expected_source_version':b.row_version,
            'expected_target_version':target.row_version,'asset_ids':[str(a.id)],'asset_versions':{str(a.id):a.row_version}})
        a.refresh_from_db();self.assertEqual(a.location,self.room.location)
        self.call(self.stock,'asset_action',{'action':'RETIRE','reason':'Retired','expected_version':a.row_version},a.id)
        self.assertEqual(StockBalance.objects.get(item=self.serial,stockroom=self.room).quantity,1)
        self.assertIsNone(StockAsset.objects.get(asset=a).stockroom_id)

    def test_managed_asset_requires_stock_role_and_warehouse_return(self):
        o=self.ready_order(self.serial,1);r=self.receive(o,1,'ONE',[{'asset_no':'S-1','serial_number':'SER-1'}])
        asset=Asset.objects.get(id=r['assets'][0]['id'])
        with self.assertRaises(s.BusinessError):
            self.call(self.admin,'asset_action',{'action':'ISSUE','person_id':str(self.employee.id),'location':'Desk','reason':'x','expected_version':1},asset.id)
        with self.assertRaises(s.BusinessError):
            self.call(self.stock,'asset_action',{'action':'MOVE','location':'Desk','reason':'x','expected_version':1},asset.id)
        self.call(self.stock,'asset_action',{'action':'ISSUE','person_id':str(self.employee.id),'location':'Desk','reason':'x','expected_version':1},asset.id)
        with self.assertRaises(s.BusinessError):
            self.call(self.stock,'asset_action',{'action':'RETURN','location':'Desk','reason':'x','expected_version':2},asset.id)
        self.assertEqual(Asset.objects.get(id=asset.id).status,'IN_USE')

    def test_serialized_validation_duplicate_asset_rollback(self):
        o=self.ready_order(self.serial,2)
        with self.assertRaises(s.BusinessError): self.receive(o,2,'WRONG',[{'asset_no':'S-1','serial_number':'1'}])
        with self.assertRaises(IntegrityError): self.receive(o,2,'DUP',[{'asset_no':'S-1','serial_number':'1'},{'asset_no':'S-1','serial_number':'2'}])
        self.assertEqual(StockAsset.objects.count(),0);self.assertEqual(GoodsReceipt.objects.count(),0)
        self.assertEqual(self.fresh(o)['received_quantity'],0)

    def test_receipt_failure_rolls_back_balances_assets_and_order(self):
        o=self.ready_order(self.serial,1)
        with patch('desk.procurement.movement',side_effect=IntegrityError('forced')):
            with self.assertRaises(IntegrityError): self.receive(o,1,'FAIL',[{'asset_no':'FAIL','serial_number':'FAIL'}])
        self.assertFalse(Asset.objects.filter(asset_no='FAIL').exists());self.assertEqual(GoodsReceipt.objects.count(),0)
        self.assertEqual(StockBalance.objects.count(),0);self.assertEqual(self.fresh(o)['received_quantity'],0)

    def test_financial_redaction_and_role_revocation(self):
        o=self.ready_order();self.client.force_login(self.stock.user)
        data=self.client.get('/api/v1/procurement/orders/'+o['id']).json()
        self.assertNotIn('unit_price',data);self.assertNotIn('total',data)
        contract=p.master_data(self.contract,self.admin);self.assertNotIn('amount',contract);self.assertNotIn('notes',contract)
        r=self.request_purchase();RoleGrant.objects.filter(person=self.buyer,role='PROCUREMENT_MANAGER').delete()
        self.assertFalse(p.request_query(self.buyer).filter(id=r['id']).exists())
        with self.assertRaises(s.BusinessError): self.approve(r)

    def test_ordinary_users_cannot_read_inventory_or_other_purchase_requests(self):
        r=self.request_purchase();self.client.force_login(self.employee.user)
        for path in ['/api/v1/inventory/balances','/api/v1/inventory/movements','/api/v1/procurement/contracts']:
            self.assertEqual(self.client.get(path).status_code,403)
        self.assertEqual(self.client.get('/api/v1/procurement/requisitions/'+r['id']).status_code,404)
        self.client.force_login(self.foreign.user)
        self.assertEqual(self.client.get('/api/v1/procurement/requisitions/'+r['id']).status_code,404)

    def test_immutable_sources_ledgers_and_cross_org_references(self):
        o=self.ready_order();self.receive(o,1,'FIRST')
        for model,field,value in [(Contract,'name','tampered'),(GoodsReceipt,'quantity',2),(StockMovement,'quantity',100),
                                   (PurchaseOrder,'quantity',100),(PurchaseRequisition,'quantity',100)]:
            with self.assertRaises(IntegrityError),transaction.atomic(): model.objects.all().update(**{field:value})
        with self.assertRaises(IntegrityError),transaction.atomic(): StockBalance.objects.all().update(quantity=-1)
        foreign_room=Stockroom.objects.create(organization=self.other_org,code='F',name='Foreign',location='F')
        with self.assertRaises(IntegrityError),transaction.atomic():
            StockBalance.objects.create(organization=self.org,stockroom=foreign_room,item=self.bulk)

    def test_master_api_and_html_pages(self):
        self.client.force_login(self.buyer.user)
        for path in ['/contracts','/procurement/requisitions','/procurement/orders','/inventory','/inventory/movements']:
            response=self.client.get(path);self.assertEqual(response.status_code,200,response.content)
        response=self.client.post('/api/v1/procurement/suppliers',data={'code':'S2','name':'New','contact':''},
            content_type='application/json',HTTP_IDEMPOTENCY_KEY='supplier')
        self.assertEqual(response.status_code,201,response.content)
        r=self.approve(self.request_purchase());o=self.release(self.draft(r))
        for person,path in [(self.manager,'/procurement/requisitions/'+r['id']),(self.stock,'/procurement/orders/'+o['id'])]:
            self.client.force_login(person.user);response=self.client.get(path);self.assertEqual(response.status_code,200,response.content)

@skipUnless(connection.vendor=='postgresql','Inventory and contract races require PostgreSQL row locks.')
class ProcurementRaceTests(SupplyFixtures,TransactionTestCase):
    def setUp(self): self.build_supply()

    def parallel(self,fn,values):
        def task(value):
            close_old_connections()
            try:
                try: fn(value);return 'success'
                except s.BusinessError as error: return error.status
            finally: close_old_connections()
        with ThreadPoolExecutor(max_workers=2) as pool: return list(pool.map(task,values))

    def test_concurrent_receipts_never_over_receive(self):
        o=self.ready_order(qty=2)
        def receive(ref):
            actor=Person.objects.get(id=self.stock.id)
            self.call(actor,'buy_receipt',{'stockroom_id':str(self.room.id),'quantity':2,'reference':ref,'serials':[],
                'reason':'race','expected_version':o['version']},o['id'])
        results=self.parallel(receive,['A','B']);self.assertEqual(results.count('success'),1);self.assertIn(409,results)
        self.assertEqual(GoodsReceipt.objects.count(),1);self.assertEqual(StockBalance.objects.get().quantity,2)

    def test_concurrent_stock_issues_never_negative(self):
        o=self.ready_order();self.receive(o,5,'ALL');b=StockBalance.objects.get()
        def issue(key):
            actor=Person.objects.get(id=self.stock.id)
            self.call(actor,'stock_issue',{'item_id':str(self.bulk.id),'source_id':str(self.room.id),'quantity':4,
                'reason':key,'expected_source_version':b.row_version,'person_id':str(self.employee.id),'destination':'Desk'})
        results=self.parallel(issue,['A','B']);self.assertEqual(results.count('success'),1);self.assertIn(409,results)
        b.refresh_from_db();self.assertEqual(b.quantity,1)

    def test_concurrent_contract_commitments_stay_within_cap(self):
        today=timezone.localdate();cap=Contract.objects.create(organization=self.org,supplier=self.supplier,code='CAP',name='Cap',
            starts_on=today,ends_on=today+timedelta(days=1),currency='KRW',amount=1000)
        orders=[self.draft(self.approve(self.request_purchase(qty=1,price='600')),price='600',contract=cap) for _ in range(2)]
        def release(o):
            actor=Person.objects.get(id=self.buyer.id)
            self.call(actor,'buy_order_action',{'action':'RELEASE','reason':'race','expected_version':o['version']},o['id'])
        results=self.parallel(release,orders);self.assertEqual(results.count('success'),1);self.assertIn(409,results)
        self.assertEqual(PurchaseOrder.objects.filter(contract=cap,status='ORDERED').count(),1)

    def test_asset_issue_and_warehouse_transfer_cannot_both_win(self):
        o=self.ready_order(self.serial,1);receipt=self.receive(o,1,'DEVICE',[{'asset_no':'RACE','serial_number':'RACE'}]);asset=Asset.objects.get(id=receipt['assets'][0]['id']);b=StockBalance.objects.get()
        def act(kind):
            actor=Person.objects.get(id=self.stock.id)
            if kind=='issue': self.call(actor,'asset_action',{'action':'ISSUE','person_id':str(self.employee.id),'location':'Desk','reason':'race','expected_version':1},asset.id)
            else: self.call(actor,'stock_transfer',{'item_id':str(self.serial.id),'source_id':str(self.room.id),'target_id':str(self.other_room.id),
                'quantity':1,'reason':'race','expected_source_version':b.row_version,'expected_target_version':0,
                'asset_ids':[str(asset.id)],'asset_versions':{str(asset.id):1}})
        results=self.parallel(act,['issue','transfer']);self.assertEqual(results.count('success'),1);self.assertIn(409,results)
        asset.refresh_from_db();total=sum(StockBalance.objects.values_list('quantity',flat=True))
        self.assertEqual(total,0 if asset.status=='IN_USE' else 1)
