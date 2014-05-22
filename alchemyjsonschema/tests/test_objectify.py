# -*- coding:utf-8 -*-
def _callFUT(*args, **kwargs):
    from alchemyjsonschema.dictify import objectify
    return objectify(*args, **kwargs)


def test_it__simple():
    from alchemyjsonschema import SchemaFactory, SingleModelWalker
    from alchemyjsonschema.dictify import ModelLookup
    import alchemyjsonschema.tests.models as models
    from datetime import datetime

    factory = SchemaFactory(SingleModelWalker)
    user_schema = factory.create(models.User)

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
    from alchemyjsonschema import SchemaFactory, SingleModelWalker, InvalidStatus
    from alchemyjsonschema.dictify import ModelLookup
    import alchemyjsonschema.tests.models as models
    from datetime import datetime
    import pytest

    factory = SchemaFactory(SingleModelWalker)
    user_schema = factory.create(models.User)

    created_at = datetime(2000, 1, 1)
    user_dict = dict(name="foo", created_at=created_at)  # pk is not found
    modellookup = ModelLookup(models)

    with pytest.raises(InvalidStatus):
        _callFUT(user_dict, user_schema, modellookup, strict=True)


def test_it__strict_false__then__required_are_notfound__ok():
    from alchemyjsonschema import SchemaFactory, SingleModelWalker
    from alchemyjsonschema.dictify import ModelLookup
    import alchemyjsonschema.tests.models as models
    from datetime import datetime

    factory = SchemaFactory(SingleModelWalker)
    user_schema = factory.create(models.User)

    created_at = datetime(2000, 1, 1)
    user_dict = dict(name="foo", created_at=created_at)  # pk is not found
    modellookup = ModelLookup(models)

    result = _callFUT(user_dict, user_schema, modellookup, strict=False)

    assert isinstance(result, models.User)
    assert result.pk is None
    assert result.name == "foo"
    assert result.created_at == datetime(2000, 1, 1)
    assert result.group_id is None


def test_it_complex():
    from alchemyjsonschema import SchemaFactory, AlsoChildrenWalker
    from alchemyjsonschema.dictify import ModelLookup
    import alchemyjsonschema.tests.models as models
    from datetime import datetime

    factory = SchemaFactory(AlsoChildrenWalker)
    user_schema = factory.create(models.User)

    created_at = datetime(2000, 1, 1)
    created_at2 = datetime(2001, 1, 1)
    group_dict = dict(name="ravenclaw", color="blue", created_at=created_at2)
    user_dict = dict(name="foo", created_at=created_at, group=group_dict)  # pk is not found
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
