# -*- coding:utf-8 -*-
def _callFUT(*args, **kwargs):
    from alchemyjsonschema.dictify import objectify
    return objectify(*args, **kwargs)


def test_it():
    from alchemyjsonschema.tests import models
    from alchemyjsonschema import SchemaFactory, AlsoChildrenWalker
    from alchemyjsonschema.dictify import ModelLookup

    factory = SchemaFactory(AlsoChildrenWalker)
    a_schema = factory(models.A0)
    modellookup = ModelLookup(models)

    params = {"name": "a0",
              "children": [
                  {"name": "a00",
                   "children": [{"name": "a000"},
                                 {"name": "a001"},
                                 {"name": "a002"}]},
                  {"name": "a10",
                   "children": [{"name": "a010"}]}]}

    result = _callFUT(params, a_schema, modellookup, strict=False)
    assert len(result.children) == 2
    assert len(result.children[0].children) == 3
    assert len(result.children[1].children) == 1
