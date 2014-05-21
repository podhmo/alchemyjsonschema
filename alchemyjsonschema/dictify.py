# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from alchemyjsonschema.tests.models import Group, User
from alchemyjsonschema import SchemaFactory, AlsoChildrenWalker

factory = SchemaFactory(AlsoChildrenWalker)
group_schema = factory.create(Group)
import pprint
pprint.pprint(group_schema)
"""
{'properties': {'color': {'enum': ['red', 'green', 'yellow', 'blue'],
                          'maxLength': 6,
                          'type': 'string'},
                'name': {'maxLength': 255, 'type': 'string'},
                'pk': {'description': 'primary key', 'type': 'integer'},
                'users': {'items': {'name': {'maxLength': 255,
                                             'type': 'string'},
                                    'pk': {'description': 'primary key',
                                           'type': 'integer'}},
                          'type': 'array'}},
 'required': ['pk', 'name'],
 'title': 'Group',
 'type': 'object'}
"""


def dictify(ob, schema):
    return dictify_properties(ob, schema["properties"])


def dictify_properties(ob, properties):
    D = {}
    for k, v in properties.items():
        D[k] = _dictify(ob, k, v)
    return D


def _dictify(ob, name, schema):
    type_ = schema["type"]
    if type_ == "array":
        return [dictify_properties(e, schema["items"]) for e in getattr(ob, name)]
    elif type_ == "object":
        return dictify_properties(getattr(ob, name), schema["properties"])
    else:
        return getattr(ob, name)
