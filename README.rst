alchemyjsonschema
=================

.. image:: https://travis-ci.org/podhmo/alchemyjsonschema.svg
  :target: https://travis-ci.org/podhmo/alchemyjsonschema.svg

features
----------------------------------------

alchemyjsonschema is the library for converting sqlalchemys's model to jsonschema.

- using alchemyjsonschema as command
- using alchemyjsonschema as library

as library
----------------------------------------

having three output styles.

- NoForeignKeyWalker -- ignore relationships
- ForeignKeyWalker -- expecting the information about relationship is foreign key
- StructuralWalker -- fullset output(expecting the information about relationship is full JSON data)

examples
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

dumping json with above three output styles.

target models are here. Group and User.

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


NoForeignKeyWalker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

   import pprint as pp
   from alchemyjsonschema import SchemaFactory
   from alchemyjsonschema import NoForeignKeyWalker

   factory = SchemaFactory(NoForeignKeyWalker)
   pp.pprint(factory(User))

   """
   {'properties': {'name': {'maxLength': 255, 'type': 'string'},
                   'pk': {'description': 'primary key', 'type': 'integer'}},
    'required': ['pk'],
    'title': 'User',
    'type': 'object'}
   """


ForeignKeyWalker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

   import pprint as pp
   from alchemyjsonschema import SchemaFactory
   from alchemyjsonschema import ForeignKeyWalker

   factory = SchemaFactory(ForeignKeyWalker)
   pp.pprint(factory(User))

   """
   {'properties': {'group_id': {'type': 'integer'},
                   'name': {'maxLength': 255, 'type': 'string'},
                   'pk': {'description': 'primary key', 'type': 'integer'}},
    'required': ['pk', 'group_id'],
    'title': 'User',
    'type': 'object'}
   """


StructuralWalker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. code:: python

   import pprint as pp
   from alchemyjsonschema import SchemaFactory
   from alchemyjsonschema import StructuralWalker

   factory = SchemaFactory(StructuralWalker)
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

as command
----------------------------------------

using alchemyjsonschema as command (the command name is also `alchemyjsonschema`).

help

.. code:: bash

    $ alchemyjsonschema --help
    usage: alchemyjsonschema [-h] [--walker {noforeignkey,foreignkey,structual}]
                             [--decision {default,fullset}] [--depth DEPTH]
                             [--out OUT]
                             target

    positional arguments:
      target                the module or class to extract schemas from

    optional arguments:
      -h, --help            show this help message and exit
      --walker {noforeignkey,foreignkey,structual}
      --decision {default,fullset}
      --depth DEPTH
      --out OUT             output to file

If above two model definitions (User,Group) are existed in `alchemyjsonschema.tests.models` .

Target is the class position or module position. for example,

- class position -- `alchemyjsonschema.tests.models:User`
- module position -- `alchemyjsonschema.tests.models`

example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using StructuralWalker via command line (--walker structural).
Of course, NoForeignKeyWalker is noforeignkey, and ForeignKeyWalker is foreignkey.

.. code:: bash

    $ alchemyjsonschema --walker structual alchemyjsonschema.tests.models:Group

    {
      "definitions": {
        "Group": {
          "properties": {
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
            "name": {
              "maxLength": 255,
              "type": "string"
            },
            "pk": {
              "description": "primary key",
              "type": "integer"
            },
            "users": {
              "items": {
                "$ref": "#/definitions/User"
              },
              "type": "array"
            }
          },
          "required": [
            "pk"
          ],
          "title": "Group",
          "type": "object"
        },
        "User": {
          "properties": {
            "created_at": {
              "format": "date-time",
              "type": "string"
            },
            "name": {
              "maxLength": 255,
              "type": "string"
            },
            "pk": {
              "description": "primary key",
              "type": "integer"
            }
          },
          "required": [
            "pk"
          ],
          "type": "object"
        }
      }
    }

Output is not same when using Walker-class, directly. This is handy output for something like a swagger(OpenAPI 2.0)'s tool.

appendix: what is `--decision` ?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

what is `--decision`? (TODO: gentle description)

.. code-block:: bash

   $ alchemyjsonschema --walker structual alchemyjsonschema.tests.models:User | jq . -S > /tmp/default.json
   $ alchemyjsonschema --decision useforeignkey --walker structual alchemyjsonschema.tests.models:User | jq . -S > /tmp/useforeignkey.json
   $ diff -u /tmp/default.json /tmp/useforeignkey.json

.. code-block:: diff

  --- /tmp/default.json	2017-01-02 22:49:44.000000000 +0900
  +++ /tmp/useforeignkey.json	2017-01-02 22:53:13.000000000 +0900
  @@ -1,43 +1,14 @@
   {
     "definitions": {
  -    "Group": {
  -      "properties": {
  -        "color": {
  -          "enum": [
  -            "red",
  -            "green",
  -            "yellow",
  -            "blue"
  -          ],
  -          "maxLength": 6,
  -          "type": "string"
  -        },
  -        "created_at": {
  -          "format": "date-time",
  -          "type": "string"
  -        },
  -        "name": {
  -          "maxLength": 255,
  -          "type": "string"
  -        },
  -        "pk": {
  -          "description": "primary key",
  -          "type": "integer"
  -        }
  -      },
  -      "required": [
  -        "pk"
  -      ],
  -      "type": "object"
  -    },
       "User": {
         "properties": {
           "created_at": {
             "format": "date-time",
             "type": "string"
           },
  -        "group": {
  -          "$ref": "#/definitions/Group"
  +        "group_id": {
  +          "relation": "group",
  +          "type": "integer"
           },
           "name": {
             "maxLength": 255,
