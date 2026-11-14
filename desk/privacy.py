"""Keep personal labels out of durable replay caches; resolve by organization at read time."""
def cache_value(value,actor=None):
    if isinstance(value,list):return [cache_value(item,actor) for item in value]
    if isinstance(value,dict):
        if 'id' in value and 'display_name' in value:return {'id':value['id'],'_person_ref':True}
        if actor and {'id','actor','recipient','asset_ids','kind'} <= set(value):
            from .models import StockMovement
            movement=StockMovement.objects.filter(id=value['id'],organization=actor.organization).first()
            if movement:
                value={**value,'_person_labels':{'actor':str(movement.actor_id),'recipient':str(movement.recipient_id) if movement.recipient_id else None}}
                value.pop('actor',None);value.pop('recipient',None)
        return {key:cache_value(item,actor) for key,item in value.items()}
    return value


def restore_value(value,actor):
    if isinstance(value,list):return [restore_value(item,actor) for item in value]
    if isinstance(value,dict):
        if value.get('_person_ref'):
            from .models import Person
            person=Person.objects.filter(organization=actor.organization,id=value['id']).first()
            return {'id':value['id'],'display_name':person.display_name if person else ''}
        result={key:restore_value(item,actor) for key,item in value.items() if key!='_person_labels'}
        if '_person_labels' in value:
            from .models import Person
            for key,id in value['_person_labels'].items():
                person=Person.objects.filter(id=id,organization=actor.organization).first() if id else None
                result[key]=person.display_name if person else None
        return result
    return value


def mask(value):
    if not value:return ''
    if '@' in value:
        left,right=value.split('@',1);return left[:1]+'***@'+right
    return value[:1]+'***'+value[-2:] if len(value)>2 else '***'
