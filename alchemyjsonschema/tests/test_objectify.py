# -*- coding:utf-8 -*-
def _callFUT(*args, **kwargs):
    from alchemyjsonschema.dictify import objectify

    return objectify(*args, **kwargs)


def test_it__simple():
    from alchemyjsonschema import SchemaFactory, ForeignKeyWalker
    from alchemyjsonschema.dictify import ModelLookup
    import alchemyjsonschema.tests.models as models
    from datetime import datetime

    factory = SchemaFactory(ForeignKeyWalker)
    user_schema = factory(models.User)

    created_at = datetime(2000, 1, 1)
    user_dict = dict(pk=1, name="foo", created_at=created_at, group_id=10)
    modellookup = ModelLookup(models)

    result = _callFUT(user_dict, user_schema, modellookup)

    assert isinstance(result, models.User)
    assert result.pk == 1
    assert result.name == "foo"
    assert result.created_at == datetime(2000, 1, 1)
    assert result.group_id == 10


def test_it__strict_true__then__required_are_notfound__error_raised():
    from alchemyjsonschema import SchemaFactory, ForeignKeyWalker, InvalidStatus
    from alchemyjsonschema.dictify import ModelLookup
    import alchemyjsonschema.tests.models as models
    from datetime import datetime
    import pytest

    factory = SchemaFactory(ForeignKeyWalker)
    user_schema = factory(models.User)

    created_at = datetime(2000, 1, 1)
    user_dict = dict(name="foo", created_at=created_at)  # pk is not found
    modellookup = ModelLookup(models)

    with pytest.raises(InvalidStatus):
        _callFUT(user_dict, user_schema, modellookup, strict=True)


def test_it__strict_false__then__required_are_notfound__ok():
    from alchemyjsonschema import SchemaFactory, ForeignKeyWalker
    from alchemyjsonschema.dictify import ModelLookup
    import alchemyjsonschema.tests.models as models
    from datetime import datetime

    factory = SchemaFactory(ForeignKeyWalker)
    user_schema = factory(models.User)

    created_at = datetime(2000, 1, 1)
    user_dict = dict(name="foo", created_at=created_at)  # pk is not found
    modellookup = ModelLookup(models)

    result = _callFUT(user_dict, user_schema, modellookup, strict=False)

    assert isinstance(result, models.User)
    assert result.pk is None
    assert result.name == "foo"
    assert result.created_at == datetime(2000, 1, 1)
    assert result.group_id is None


def test_it_complex__relation_decision():
    from alchemyjsonschema import SchemaFactory, StructuralWalker, RelationDesicion
    from alchemyjsonschema.dictify import ModelLookup
    import alchemyjsonschema.tests.models as models
    from datetime import datetime

    factory = SchemaFactory(StructuralWalker, relation_decision=RelationDesicion())
    user_schema = factory(models.User)

    created_at = datetime(2000, 1, 1)
    created_at2 = datetime(2001, 1, 1)
    group_dict = dict(name="ravenclaw", color="blue", created_at=created_at2)
    user_dict = dict(
        name="foo", created_at=created_at, group=group_dict
    )  # pk is not found
    modellookup = ModelLookup(models)

    result = _callFUT(user_dict, user_schema, modellookup, strict=False)

    assert isinstance(result, models.User)
    assert result.pk is None
    assert result.name == "foo"
    assert result.created_at == datetime(2000, 1, 1)
    assert result.group_id is None

    assert isinstance(result.group, models.Group)
    assert result.group.name == "ravenclaw"
    assert result.group.color == "blue"
    assert result.group.created_at == created_at2

    assert modellookup.name_stack == []


def test_it_complex__fullset_decision():
    from alchemyjsonschema import (
        SchemaFactory,
        StructuralWalker,
        UseForeignKeyIfPossibleDecision,
    )
    from alchemyjsonschema.dictify import ModelLookup
    import alchemyjsonschema.tests.models as models
    from datetime import datetime

    factory = SchemaFactory(
        StructuralWalker, relation_decision=UseForeignKeyIfPossibleDecision()
    )
    user_schema = factory(models.User)

    created_at = datetime(2000, 1, 1)
    user_dict = dict(name="foo", created_at=created_at, group_id=1)  # pk is not found
    modellookup = ModelLookup(models)

    result = _callFUT(user_dict, user_schema, modellookup, strict=False)

    assert isinstance(result, models.User)
    assert result.pk is None
    assert result.name == "foo"
    assert result.created_at == datetime(2000, 1, 1)
    assert result.group_id == 1
    assert modellookup.name_stack == []


def test_it_complex2():
    from alchemyjsonschema import SchemaFactory, StructuralWalker
    from alchemyjsonschema.dictify import ModelLookup
    import alchemyjsonschema.tests.models as models
    from datetime import datetime

    factory = SchemaFactory(StructuralWalker)
    group_schema = factory(models.Group)

    created_at = datetime(2000, 1, 1)
    created_at2 = datetime(2001, 1, 1)
    user_dict = dict(name="foo", created_at=created_at)  # pk is not found
    group_dict = dict(
        name="ravenclaw", color="blue", created_at=created_at2, users=[user_dict]
    )
    modellookup = ModelLookup(models)

    result = _callFUT(group_dict, group_schema, modellookup, strict=False)

    assert isinstance(result, models.Group)
    assert result.pk is None
    assert result.name == "ravenclaw"
    assert result.color == "blue"
    assert result.created_at == datetime(2001, 1, 1)

    assert isinstance(result.users[0], models.User)
    assert result.users[0].name == "foo"
    assert result.users[0].created_at == created_at

    assert modellookup.name_stack == []


def test_it_complex__partial():
    from alchemyjsonschema import SchemaFactory, StructuralWalker
    from alchemyjsonschema.dictify import ModelLookup
    import alchemyjsonschema.tests.models as models
    from datetime import datetime

    factory = SchemaFactory(StructuralWalker)
    user_schema = factory(models.User)

    created_at = datetime(2000, 1, 1)
    user_dict = dict(name="foo", created_at=created_at)
    modellookup = ModelLookup(models)

    result = _callFUT(user_dict, user_schema, modellookup, strict=False)

    assert isinstance(result, models.User)
    assert result.pk is None
    assert result.name == "foo"
    assert result.created_at == datetime(2000, 1, 1)
    assert result.group_id is None

    assert modellookup.name_stack == []


def test_it_complex__partial2():
    from alchemyjsonschema import SchemaFactory, StructuralWalker
    from alchemyjsonschema.dictify import ModelLookup
    import alchemyjsonschema.tests.models as models
    from datetime import datetime

    factory = SchemaFactory(StructuralWalker)
    group_schema = factory(models.Group)

    created_at2 = datetime(2001, 1, 1)
    group_dict = dict(name="ravenclaw", color="blue", created_at=created_at2)
    modellookup = ModelLookup(models)

    result = _callFUT(group_dict, group_schema, modellookup, strict=False)

    assert isinstance(result, models.Group)
    assert result.pk is None
    assert result.name == "ravenclaw"
    assert result.color == "blue"
    assert result.created_at == datetime(2001, 1, 1)

    assert modellookup.name_stack == []


def test_it_complex__partia3():
    from alchemyjsonschema import SchemaFactory, StructuralWalker
    from alchemyjsonschema.dictify import ModelLookup
    import alchemyjsonschema.tests.models as models
    from datetime import datetime

    factory = SchemaFactory(StructuralWalker)
    user_schema = factory(models.User)

    created_at = datetime(2000, 1, 1)
    user_dict = dict(name="foo", created_at=created_at, group={})
    modellookup = ModelLookup(models)

    result = _callFUT(user_dict, user_schema, modellookup, strict=False)

    assert isinstance(result, models.User)
    assert result.pk is None
    assert result.name == "foo"
    assert result.created_at == datetime(2000, 1, 1)
    assert result.group_id is None

    assert modellookup.name_stack == []


def test_it_complex__partial4():
    from alchemyjsonschema import SchemaFactory, StructuralWalker
    from alchemyjsonschema.dictify import ModelLookup
    import alchemyjsonschema.tests.models as models
    from datetime import datetime

    factory = SchemaFactory(StructuralWalker)
    group_schema = factory(models.Group)

    created_at2 = datetime(2001, 1, 1)
    group_dict = dict(name="ravenclaw", color="blue", created_at=created_at2, users=[])
    modellookup = ModelLookup(models)

    result = _callFUT(group_dict, group_schema, modellookup, strict=False)

    assert isinstance(result, models.Group)
    assert result.pk is None
    assert result.name == "ravenclaw"
    assert result.color == "blue"
    assert result.created_at == datetime(2001, 1, 1)

    assert modellookup.name_stack == []


def test_it_nested():
    from alchemyjsonschema.tests import models
    from alchemyjsonschema import SchemaFactory, StructuralWalker
    from alchemyjsonschema.dictify import ModelLookup

    factory = SchemaFactory(StructuralWalker)
    a_schema = factory(models.A0)
    modellookup = ModelLookup(models)

    params = {
        "name": "a0",
        "children": [
            {
                "name": "a00",
                "children": [{"name": "a000"}, {"name": "a001"}, {"name": "a002"}],
            },
            {"name": "a10", "children": [{"name": "a010"}]},
        ],
    }

    result = _callFUT(params, a_schema, modellookup, strict=False)
    assert len(result.children) == 2
    assert len(result.children[0].children) == 3
    assert len(result.children[1].children) == 1
