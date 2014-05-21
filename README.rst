alchemyjsonschema
=================

.. code:: python

   # -*- coding:utf-8 -*-
   import sqlalchemy as sa
   import sqlalchemy.orm as orm
   from sqlalchemy.ext.declarative import declarative_base

   Base = declarative_base()


   class Group(Base):
       """model for test"""
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
   pp.pprint(factory.create(User))

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
   pp.pprint(factory.create(User))

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
   pp.pprint(factory.create(User))

   """
   {'properties': {'group': {'name': {'maxLength': 255, 'type': 'string'},
                             'pk': {'description': 'primary key',
                                    'type': 'integer'}},
                   'name': {'maxLength': 255, 'type': 'string'},
                   'pk': {'description': 'primary key', 'type': 'integer'}},
    'required': ['pk'],
    'title': 'User',
    'type': 'object'}
   """

   pp.pprint(factory.create(Group))

   """
   {'description': 'model for test',
    'properties': {'name': {'maxLength': 255, 'type': 'string'},
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
