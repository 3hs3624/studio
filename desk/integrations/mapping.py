import json,re
from datetime import date
import xml.etree.ElementTree as ET

class MappingError(ValueError):pass
MISSING=object()

def path(data,value):
    if value in ('','$'):return data
    value=value.removeprefix('$.')
    if len(value)>300 or any(not re.fullmatch(r'[A-Za-z0-9_\-]+',part) for part in value.split('.')):raise MappingError('INVALID_MAPPING_PATH')
    for part in value.split('.'):
        if isinstance(data,dict):data=data.get(part,MISSING)
        elif isinstance(data,list) and part.isdigit() and int(part)<len(data):data=data[int(part)]
        else:return MISSING
        if data is MISSING:return MISSING
    return data

def rules_validate(rules):
    if not isinstance(rules,dict) or len(rules)>100:raise MappingError('MAPPING_LIMIT')
    allowed={'path','transform','default','required','code_map'}
    for key,rule in rules.items():
        if not isinstance(key,str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,79}',key) or not isinstance(rule,dict) or set(rule)-allowed:raise MappingError('INVALID_MAPPING')
        if not isinstance(rule.get('path',''),str):raise MappingError('INVALID_MAPPING_PATH')
        path({},rule.get('path',''))
        if rule.get('transform','COPY') not in ('COPY','STRING','NUMBER','BOOLEAN','TRIM','UPPER','LOWER','DATE'):raise MappingError('INVALID_TRANSFORM')
        if type(rule.get('required',False)) is not bool or not isinstance(rule.get('code_map',{}),dict) or len(rule.get('code_map',{}))>200:raise MappingError('INVALID_MAPPING')
    return rules

def apply(data,rules):
    result={}
    for key,rule in rules.items():
        value=path(data,rule.get('path',''))
        if value is MISSING:value=rule.get('default',MISSING)
        if value is MISSING:
            if rule.get('required'):raise MappingError('MISSING_REQUIRED_VALUE')
            continue
        code_map=rule.get('code_map',{})
        if code_map:
            if not isinstance(value,(str,int,float,bool)):raise MappingError('CODE_LOOKUP_TYPE')
            value=code_map.get(str(value),value)
        type_=rule.get('transform','COPY')
        try:
            if type_=='STRING':value=str(value)
            elif type_=='NUMBER':
                if isinstance(value,bool):raise ValueError()
                value=float(value)
                if value!=value or abs(value)>10**15:raise ValueError()
                if value.is_integer():value=int(value)
            elif type_=='BOOLEAN':
                if value not in (True,False,'true','false','Y','N',1,0):raise ValueError()
                value=value in (True,'true','Y',1)
            elif type_ in ('TRIM','UPPER','LOWER'):
                if not isinstance(value,str):raise ValueError()
                value={'TRIM':str.strip,'UPPER':str.upper,'LOWER':str.lower}[type_](value)
            elif type_=='DATE':value=date.fromisoformat(value).isoformat()
        except (ValueError,TypeError,OverflowError):raise MappingError('VALUE_CONVERSION_FAILED') from None
        result[key]=value
    return result

def parse_xml(payload):
    if b'<!DOCTYPE' in payload.upper() or b'<!ENTITY' in payload.upper():raise MappingError('UNSAFE_XML')
    try:root=ET.fromstring(payload)
    except ET.ParseError:raise MappingError('INVALID_XML') from None
    def convert(node,depth=0):
        if depth>30:raise MappingError('XML_DEPTH_LIMIT')
        if not len(node):return node.text or ''
        values={};names={}
        for child in node:
            key=child.tag.split('}')[-1]
            if key in names and names[key]!=child.tag:raise MappingError('XML_NAMESPACE_COLLISION')
            names[key]=child.tag;value=convert(child,depth+1)
            if key in values:
                if not isinstance(values[key],list):values[key]=[values[key]]
                values[key].append(value)
            else:values[key]=value
        return values
    return {root.tag.split('}')[-1]:convert(root)}

def render(value,inputs,depth=0):
    if depth>10:raise MappingError('TEMPLATE_DEPTH_LIMIT')
    if isinstance(value,dict):return {key:render(item,inputs,depth+1) for key,item in value.items()}
    if isinstance(value,list):return [render(item,inputs,depth+1) for item in value]
    if isinstance(value,str) and re.fullmatch(r'\{\{[A-Za-z][A-Za-z0-9_]*\}\}',value):
        key=value[2:-2]
        if key not in inputs:raise MappingError('MISSING_TEMPLATE_VALUE')
        return inputs[key]
    return value
