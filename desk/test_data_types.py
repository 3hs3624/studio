"""Boundary tests for the shared entity/workflow type contract."""
from django.test import SimpleTestCase
from django.template.loader import render_to_string
from .data_types import scalar,metadata,catalogue,SCREEN_TYPES
from .process_engine import fields_validate,values_validate
from .services import BusinessError

class DataTypeTests(SimpleTestCase):
    def test_decimal_precision_is_preserved_and_bounds_enforced(self):
        field=dict(type='decimal',precision=20,scale=4)
        self.assertEqual(scalar(field,'1234567890123456.1234'),'1234567890123456.1234')
        for value in ('12345678901234567.1234','0.12345','NaN','Infinity',1.2,'1e999999'):
            with self.subTest(value=value),self.assertRaises(BusinessError):scalar(field,value)
    def test_metadata_rejects_wrong_type_and_invalid_ranges(self):
        for field in (dict(type='integer',max_length=20),dict(type='decimal',precision=2,scale=3),dict(type='decimal',precision=True),dict(type='text',max_length=0)):
            with self.subTest(field=field),self.assertRaises(BusinessError):metadata(field)
    def test_json_limits_and_entityset(self):
        self.assertEqual(scalar(dict(type='json'),{'ok':[False,0]}),{'ok':[False,0]})
        for value in ({'bad':float('nan')},{1:'not a JSON key'},'{}'):
            with self.assertRaises(BusinessError):scalar(dict(type='json'),value)
        with self.assertRaises(BusinessError):scalar(dict(type='entityset'),{})
        with self.assertRaises(BusinessError):scalar(dict(type='json'),{'text':'a'*65536})
    def test_date_and_timezone_validation(self):
        for kind,value in [('date','2026-02-30'),('datetime','2026-11-15T10:00:00'),('time','25:00'),('month','2026-13'),('year','0000')]:
            with self.subTest(kind=kind),self.assertRaises(BusinessError):scalar(dict(type=kind),value)
        self.assertEqual(scalar(dict(type='datetime'),'2026-11-15T10:00:00+09:00'),'2026-11-15T10:00:00+09:00')
    def test_workflow_shares_contract_without_float_conversion(self):
        fields=fields_validate([dict(key='cost',label='금액',type='decimal',precision=20,scale=4,required=True)])
        self.assertEqual(values_validate(fields,dict(cost='1234567890123456.1234'))['cost'],'1234567890123456.1234')
        with self.assertRaises(BusinessError):values_validate(fields,dict(cost='0.00001'))
        with self.assertRaises(BusinessError):values_validate(fields,dict(cost=''))
    def test_legacy_text_limit_is_preserved(self):
        field=dict(key='text',label='내용',type='text',required=False)
        with self.assertRaises(BusinessError):values_validate([field],dict(text='a'*2001))
    def test_extended_runtime_templates_escape_values(self):
        for kind in SCREEN_TYPES-{'person'}:
            html=render_to_string('desk/process-field.html',{'field':dict(key='test',type=kind,label='<script>',value='',required=False)})
            self.assertIn('&lt;script&gt;',html)
            self.assertIn('data-process-type="'+kind+'"',html)
        self.assertEqual(len({t['key'] for t in catalogue()}),len(catalogue()))

    def test_defaults_only_apply_at_creation(self):
        fields=fields_validate([dict(key='flag',label='기본값',type='boolean',required=False,default=False)])
        self.assertEqual(values_validate(fields,{},apply_defaults=True),{'flag':False})
        self.assertEqual(values_validate(fields,{},False),{})
        self.assertEqual(values_validate(fields,{'flag':True},apply_defaults=True),{'flag':True})
        with self.assertRaises(BusinessError):metadata(dict(type='date',default_function='CURRENT_TIMESTAMP'))
        with self.assertRaises(BusinessError):metadata(dict(type='text',default_function='NOW(); DROP TABLE x'))
        self.assertIn('T',values_validate([dict(key='at',label='시간',type='datetime',required=True,default_function='CURRENT_TIMESTAMP')],{},apply_defaults=True)['at'])
    def test_decimal_conditions_compare_numerically(self):
        from .process_engine import condition_match
        fields=[dict(key='cost',type='decimal')]
        self.assertTrue(condition_match({'cost':'10.00'},dict(field='cost',op='gt',value='2'),fields))
        self.assertTrue(condition_match({'cost':'2.00'},dict(field='cost',op='eq',value='2'),fields))
        self.assertFalse(condition_match({'cost':'2.00'},dict(field='cost',op='gt',value='10'),fields))
    def test_large_integer_number_rejected_without_overflow(self):
        with self.assertRaises(BusinessError):scalar(dict(type='number'),10**400)

    def test_impact_report_detects_removed_and_narrowed_fields(self):
        from .configuration_impact import field_changes
        before=[dict(key='name',type='text',max_length=100,required=False),dict(key='old',type='integer')]
        after=[dict(key='name',type='text',max_length=20,required=False),dict(key='new',type='text',required=True)]
        changes={v['key']:v for v in field_changes(before,after)}
        self.assertEqual(changes['name']['risk'],'주의')
        self.assertEqual(changes['old']['kind'],'제거')
        self.assertEqual(changes['new']['kind'],'추가')

    def test_invalid_saved_draft_does_not_break_impact_page(self):
        from .configuration_impact import field_changes
        self.assertEqual(field_changes([],None),[])
        self.assertEqual(field_changes([],['bad',None,{}]),[])

    def test_invalid_draft_contract_is_not_used_by_impact_report(self):
        from types import SimpleNamespace
        from .configuration_impact import process_impact
        self.assertEqual(process_impact(SimpleNamespace(validation_errors=['길이 오류'])),dict(changes=[],references=[],active_runs=0))
