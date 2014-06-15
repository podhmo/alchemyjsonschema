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

   pp.pprint(factory.create(Group))

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


has alchemyjsonschema command
----------------------------------------

help

.. code:: bash

    $ alchemyjsonschema -h
    usage: alchemyjsonschema [-h]
                             [--walker {noforeignkey,foreignkey,structual,control}]
                             [--depth DEPTH]
                             [--decision-relationship DECISION_RELATIONSHIP]
                             [--decision-foreignkey DECISION_FOREIGNKEY]
                             model

    positional arguments:
      model

    optional arguments:
      -h, --help            show this help message and exit
      --walker {noforeignkey,foreignkey,structual,control}
      --depth DEPTH
      --decision-relationship DECISION_RELATIONSHIP
      --decision-foreignkey DECISION_FOREIGNKEY

target models

.. code:: python

    class Group(Base):
        __tablename__ = "Group"
        query = Session.query_property()

        pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
        name = sa.Column(sa.String(255), default="", nullable=False)
        color = sa.Column(sa.Enum("red", "green", "yellow", "blue"))
        created_at = sa.Column(sa.DateTime, nullable=True)


    class User(Base):
        __tablename__ = "User"
        query = Session.query_property()

        pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
        name = sa.Column(sa.String(255), default="", nullable=False)
        group_id = sa.Column(sa.Integer, sa.ForeignKey(Group.pk), nullable=False)
        group = orm.relationship(Group, uselist=False, backref="users")
        created_at = sa.Column(sa.DateTime, nullable=True)


dump schema (commandline)

.. code:: bash

    $ alchemyjsonschema alchemyjsonschema.tests.models:Group --walker structual

    {
      "required": [
        "pk",
        "name"
      ],
      "definitions": {
        "User": {
          "type": "object",
          "properties": {
            "pk": {
              "type": "integer",
              "description": "primary key"
            },
            "name": {
              "maxLength": 255,
              "type": "string"
            },
            "created_at": {
              "format": "date-time",
              "type": "string"
            }
          }
        }
      },
      "title": "Group",
      "type": "object",
      "properties": {
        "pk": {
          "type": "integer",
          "description": "primary key"
        },
        "name": {
          "maxLength": 255,
          "type": "string"
        },
        "color": {
          "enum": [
            "red",
            "green",
            "yellow",
            "blue"
          ],
          "maxLength": 6,
          "type": "string"
        },
        "created_at": {
          "format": "date-time",
          "type": "string"
        },
        "users": {
          "items": {
            "$ref": "#/definitions/User"
          },
          "type": "array"
        }
      }
    }
