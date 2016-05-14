# -*- coding:utf-8 -*-
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Group(Base):
    __tablename__ = "Group"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    name = sa.Column(sa.String(255), default="", nullable=False)


class User(Base):
    __tablename__ = "User"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    name = sa.Column(sa.String(255), default="", nullable=True)
    group_id = sa.Column(sa.Integer, sa.ForeignKey(Group.pk), nullable=False)
    group = orm.relationship(Group, uselist=False, backref="users")


## ------SingleModelWalker--------
import pprint as pp
from alchemyjsonschema import SchemaFactory
from alchemyjsonschema import SingleModelWalker

factory = SchemaFactory(SingleModelWalker)
pp.pprint(factory(User))

"""
{'properties': {'group_id': {'type': 'integer'},
                'name': {'maxLength': 255, 'type': 'string'},
                'pk': {'description': 'primary key', 'type': 'integer'}},
 'required': ['pk', 'group_id'],
 'title': 'User',
 'type': 'object'}
"""


## ------OneModelOnlyWalker--------
import pprint as pp
from alchemyjsonschema import SchemaFactory
from alchemyjsonschema import OneModelOnlyWalker

factory = SchemaFactory(OneModelOnlyWalker)
pp.pprint(factory(User))

"""
{'properties': {'name': {'maxLength': 255, 'type': 'string'},
                'pk': {'description': 'primary key', 'type': 'integer'}},
 'required': ['pk'],
 'title': 'User',
 'type': 'object'}
"""


## ------AlsoChildrenWalker--------
import pprint as pp
from alchemyjsonschema import SchemaFactory
from alchemyjsonschema import AlsoChildrenWalker

factory = SchemaFactory(AlsoChildrenWalker)
pp.pprint(factory(User))

"""
{'definitions': {'Group': {'properties': {'pk': {'description': 'primary key',
                                                 'type': 'integer'},
                                          'name': {'maxLength': 255,
                                                   'type': 'string'}},
                           'type': 'object'}},
 'properties': {'pk': {'description': 'primary key', 'type': 'integer'},
                'name': {'maxLength': 255, 'type': 'string'},
                'group': {'$ref': '#/definitions/Group'}},
 'required': ['pk'],
 'title': 'User',
 'type': 'object'}
"""

pp.pprint(factory(Group))

"""
{'definitions': {'User': {'properties': {'pk': {'description': 'primary key',
                                                'type': 'integer'},
                                         'name': {'maxLength': 255,
                                                  'type': 'string'}},
                          'type': 'object'}},
 'description': 'model for test',
 'properties': {'pk': {'description': 'primary key', 'type': 'integer'},
                'name': {'maxLength': 255, 'type': 'string'},
                'users': {'items': {'$ref': '#/definitions/User'},
                          'type': 'array'}},
 'required': ['pk', 'name'],
 'title': 'Group',
 'type': 'object'}
"""
