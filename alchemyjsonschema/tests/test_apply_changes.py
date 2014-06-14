# -*- coding:utf-8 -*-
def _callFUT(*args, **kwargs):
    from alchemyjsonschema.dictify import apply_changes
    return apply_changes(*args, **kwargs)


def test_it_update_parent__onlyone():
    from alchemyjsonschema.tests import models as m
    from alchemyjsonschema import SchemaFactory, OneModelOnlyWalker
    from alchemyjsonschema.dictify import ModelLookup

    factory = SchemaFactory(OneModelOnlyWalker)
    a_schema = factory(m.A0)
    modellookup = ModelLookup(m)

    a0 = m.A0(pk=1, name="a0", children=[m.A1(pk=1, name="a00"), m.A1(pk=2, name=("a01"))])

    assert a0.name == "a0"
    params = {"pk": 1, "name": "updated"}
    _callFUT(a0, params, a_schema, modellookup)
    assert a0.name == "updated"
    assert len(a0.children) == 2


def test_it_update_parent__full():
    from alchemyjsonschema.tests import models as m
    from alchemyjsonschema import SchemaFactory, AlsoChildrenWalker
    from alchemyjsonschema.dictify import ModelLookup

    factory = SchemaFactory(AlsoChildrenWalker)
    a_schema = factory(m.A0)
    modellookup = ModelLookup(m)

    a0 = m.A0(pk=1, name="a0", children=[m.A1(pk=1, name="a00"), m.A1(pk=2, name=("a01"))])

    assert a0.name == "a0"
    params = {"pk": 1, "name": "updated", "children": [{"name": "a00", "pk": 1}, {"name": "a01", "pk": 2}]}
    _callFUT(a0, params, a_schema, modellookup)
    assert a0.name == "updated"


def test_it_create_child():
    from alchemyjsonschema.tests import models as m
    from alchemyjsonschema import SchemaFactory, AlsoChildrenWalker
    from alchemyjsonschema.dictify import ModelLookup

    factory = SchemaFactory(AlsoChildrenWalker)
    a_schema = factory(m.A0)
    modellookup = ModelLookup(m)

    a0 = m.A0(pk=1, name="a0", children=[m.A1(pk=1, name="a00"), m.A1(pk=2, name=("a01"))])

    assert len(a0.children) == 2
    params = {"pk": 1, "name": "a0", "children": [{"name": "new"}, {"name": "a00", "pk": 1}, {"name": "update", "pk": 2}]}
    _callFUT(a0, params, a_schema, modellookup)
    assert len(a0.children) == 3


def test_it_update_child():
    from alchemyjsonschema.tests import models as m
    from alchemyjsonschema import SchemaFactory, AlsoChildrenWalker
    from alchemyjsonschema.dictify import ModelLookup

    factory = SchemaFactory(AlsoChildrenWalker)
    a_schema = factory(m.A0)
    modellookup = ModelLookup(m)

    a0 = m.A0(pk=1, name="a0", children=[m.A1(pk=1, name="a00"), m.A1(pk=2, name=("a01"))])

    assert len(a0.children) == 2
    params = {"pk": 1, "name": "a0", "children": [{"name": "a00", "pk": 1}, {"name": "update", "pk": 2}]}
    _callFUT(a0, params, a_schema, modellookup)
    assert len(a0.children) == 2
    assert a0.children[1].name == "update"


def test_it_delete_child():
    from alchemyjsonschema.tests import models as m
    from alchemyjsonschema import SchemaFactory, AlsoChildrenWalker
    from alchemyjsonschema.dictify import ModelLookup

    factory = SchemaFactory(AlsoChildrenWalker)
    a_schema = factory(m.A0)
    modellookup = ModelLookup(m)

    a0 = m.A0(pk=1, name="a0", children=[m.A1(pk=1, name="a00"), m.A1(pk=2, name=("a01"))])

    assert len(a0.children) == 2
    params = {"pk": 1, "name": "a0", "children": [{"name": "a00", "pk": 1}]}
    _callFUT(a0, params, a_schema, modellookup)
    assert len(a0.children) == 1


def test_it_reverse_update():
    from alchemyjsonschema.tests import models as m
    from alchemyjsonschema import SchemaFactory, AlsoChildrenWalker
    from alchemyjsonschema.dictify import ModelLookup

    factory = SchemaFactory(AlsoChildrenWalker)
    a_schema = factory(m.A1)
    modellookup = ModelLookup(m)

    a0 = m.A0(pk=1, name="a0", children=[m.A1(pk=1, name="a00"), m.A1(pk=2, name=("a01"))])

    assert a0.name == "a0"
    params = {"pk": 1, "name": "a00", "parent": {"name": "updated", "pk": 1}}
    _callFUT(a0.children[0], params, a_schema, modellookup)
    assert a0.name == "updated"


# def test_it_complex():
#     pass
