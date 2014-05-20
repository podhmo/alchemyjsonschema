# -*- coding:utf-8 -*-
import sqlalchemy.types as t
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.sql.visitors import VisitableType

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
"""

## tentative
default_mapping = {
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
    t.Enum:"string", 
}


## restriction
def string_max_length(column, sub):
    sub["maxLength"] = column.type.length

def enum_one_of(column, sub):
    sub["oneOf"] = column.type.enums

default_restriction_dict = {
    t.String: string_max_length, 
    t.Enum: enum_one_of
}

class Classifier(object):
    def __init__(self, mapping=default_mapping):
        self.mapping = mapping

    def __getitem__(self, k):
        cls = k.__class__
        v = self.mapping.get(cls)
        if v is not None:
            return cls, v
        ## inheritance
        for type_ in self.mapping:
            if issubclass(cls, type_): #xxx:
                return type_, self.mapping[type_]
        raise Exception("notfound")

DefaultClassfier = Classifier(default_mapping)

class BaseModelWalker(object):
    def __init__(self, model, includes=None, excludes=None):
        self.mapper = inspect(model).mapper
        self.includes = includes
        self.excludes = excludes
        if includes and excludes:
            if set(includes).intersect(excludes):
                raise ValueError("Conflict includes={}, exclude={}".format(includes, excludes))

class SingleModelWalker(BaseModelWalker):
    def walk(self):
        for prop in self.mapper.attrs:
            if isinstance(prop, ColumnProperty):
                if self.includes is None or prop.key in self.includes:
                    if self.excludes is None or not prop.key in self.excludes:
                        yield prop

class OneModelOnlyWalker(BaseModelWalker):
    def walk(self):
        for prop in self.mapper.attrs:
            if isinstance(prop, ColumnProperty):
                if self.includes is None or prop.key in self.includes:
                    if self.excludes is None or not prop.key in self.excludes:
                        if not any(c.foreign_keys for c in prop.columns):
                            yield prop



class SchemaFactory(object):
    def __init__(self, walker, classifier=DefaultClassfier, restriction_dict=default_restriction_dict):
        self.classifier = classifier
        self.walker = walker #class
        self.restriction_dict = restriction_dict

    def create(self, model, includes=None, excludes=None):
        walker = self.walker(model, includes=includes, excludes=excludes)

        schema = {
            "title": model.__name__, 
            "type": "object", 
            "properties": self._build_properties(walker)
        }
        if model.__doc__:
            schema["description"] = model.__doc__

        required = self._detect_required(walker)

        if required:
            schema["required"] = required
        return schema

    def _build_properties(self, walker):
        D = {}
        for prop in walker.walk():
            for c in prop.columns:
                sub = {}
                if type(c.type) != VisitableType:
                    itype, sub["type"] = self.classifier[c.type]
                    for tcls in itype.__mro__:
                        fn = self.restriction_dict.get(tcls)
                        if fn is not None:
                            fn(c, sub)

                    if c.doc:
                        sub["description"] = c.doc
                    D[c.name] = sub
                else:
                    raise NotImplemented
            D[prop.key] = sub
        return D

    def _detect_required(self, walker):
        return [prop.key for prop in walker.walk() if any(not c.nullable for c in prop.columns)]
