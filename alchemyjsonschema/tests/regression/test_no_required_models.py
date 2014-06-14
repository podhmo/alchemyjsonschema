# -*- coding:utf-8 -*-
def _callFUT(*args, **kwargs):
    from alchemyjsonschema.dictify import objectify
    return objectify(*args, **kwargs)


def test_no_required():
    from alchemyjsonschema import AlsoChildrenWalker, SchemaFactory
    from alchemyjsonschema.dictify import ModelLookup
    from alchemyjsonschema.tests import models
    schema_factory = SchemaFactory(AlsoChildrenWalker)
    schema = schema_factory(models.MyModel, excludes=["id"])
    modellookup = ModelLookup(models)

    params = {"name": "foo", "value": 1}
    _callFUT(params, schema, modellookup)
