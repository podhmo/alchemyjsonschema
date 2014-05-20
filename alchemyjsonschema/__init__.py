# -*- coding:utf-8 -*-
import sqlalchemy.types as t
import jsonschema
"""
http://json-schema.org/latest/json-schema-core.html#anchor8
3.5.  JSON Schema primitive types

JSON Schema defines seven primitive types for JSON values:

    array
        A JSON array. 
    boolean
        A JSON boolean. 
    integer
        A JSON number without a fraction or exponent part. 
    number
        Any JSON number. Number includes integer. 
    null
        The JSON null value. 
    object
        A JSON object. 
    string
        A JSON string. 

// sample
{
	"title": "Example Schema",
	"type": "object",
	"properties": {
		"firstName": {
			"type": "string"
		},
		"lastName": {
			"type": "string"
		},
		"age": {
			"description": "Age in years",
			"type": "integer",
			"minimum": 0
		}
	},
	"required": ["firstName", "lastName"]
}
"""

## tentative
default_classfier = {
    t.INTEGER: "integer",
    t.INT: "integer", 
    t.CHAR: "string", 
    t.VARCHAR: "string", 
    t.NVARCHAR: "string", 
    t.TEXT: "string", 
    t.BLOB: "xxx", 
    t.CLOB: "xxx", 
    t.BINARY: "xxx", 
    t.VARBINARY: "xxx", 
    t.BOOLEAN: "boolean", 
    t.BIGINT: "integer", 
    t.SMALLINT: "integer", 
    t.INTEGER: "integer", 
    t.DATE: "date", 
    t.FLOAT: "number",
    t.NUMERIC: "integer", #xxx:
    t.REAL: "number", 
    t.DECIMAL: "integer", 
    t.TIMESTAMP: "xxx", 
    t.DATETIME: "date-time", 
    t.DATE: "date", 
    t.TIME: "time",
    t.String: "string", 
    t.Text: "string", 
    t.Integer: "integer", 
    t.SmallInteger: "integer", 
    t.BigInteger: "integer", 
    t.Numeric: "integer", 
    t.Float: "number", 
    t.DateTime: "date-time", 
    t.Date: "date", 
    t.Time: "time",
    t.LargeBinary:"xxx", 
    t.Binary:"xxx", 
    t.Boolean:"boolean", 
    t.Unicode:"string", 
    t.Concatenable:"xxx", 
    t.UnicodeText:"string", 
    t.Interval:"xxx", 
    t.Enum:"xxx", 
}

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import scoped_session, sessionmaker

Session = scoped_session(sessionmaker())
engine = sa.create_engine('sqlite://')
Session.configure(bind=engine)

Base = declarative_base(bind=engine)

class User(Base):
    __tablename__ = "User"
    query = Session.query_property()

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    name = sa.Column(sa.String(255), default="", nullable=False)
    value = sa.Column(sa.String(255), default="", nullable=False)

from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.sql.visitors import VisitableType

class SingleModelWalker(object):
    def __init__(self, model):
        self.mapper = inspect(model).mapper

    def walk(self):
        for prop in self.mapper.attrs:
            if isinstance(prop, ColumnProperty):
                yield prop

class SchemaFactory(object):
    def __init__(self, walker, classifier=default_classfier):
        self.classifier = classifier
        self.walker = walker #class

    def create(self, model):
        walker = self.walker(model)

        schema = {
            "title": model.__name__, 
            "type": "object", 
            "properties": self._build_properties(walker)
        }
        required = self._detect_required(walker)
        if required:
            schema["required"] = required
        return schema

    def _build_properties(self, walker):
        D = {}
        for prop in walker.walk():
            sub = {}
            types_list = tuple((c.type.__class__ if type(c.type) != VisitableType else c.type)
                               for c in prop.columns)
            types = [self.classifier[t] for t in types_list]
            assert len(types) == 1 #xxx:
            sub["type"] = types[0]
            if prop.doc:
                sub["description"] = prop.doc
            D[prop.key] = sub
        return D

    def _detect_required(self, walker):
        return [prop.key for prop in walker.walk() if any(not c.nullable for c in prop.columns)]

factory = SchemaFactory(SingleModelWalker, default_classfier)
import json
pp = lambda d : json.dumps(d, indent=2, ensure_ascii=False)
print(pp(factory.create(User)))

schema = factory.create(User)

from jsonschema import validate
print(validate({"pk": 1, "name": "foo", "value": "bar"}, schema))
Base.metadata.create_all()


