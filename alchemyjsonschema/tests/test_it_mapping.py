# -*- coding:utf-8 -*-
"""
jsondict <-> dict <-> model object
   \______________________/
"""


def _datetime(*args):
    import pytz
    from datetime import datetime
    args = list(args)
    args.append(pytz.utc)
    return datetime(*args)


def _getTarget():
    from alchemyjsonschema.mapping import Draft4MappingFactory
    return Draft4MappingFactory


def _makeOne(schema_factory, model, *args, **kwargs):
    import alchemyjsonschema.tests.models as models
    module = models
    mapping_factory = _getTarget()(schema_factory, module, *args, **kwargs)
    return mapping_factory.create(model)


def test_it__dict_from_model_object():
    from alchemyjsonschema import AlsoChildrenWalker, SchemaFactory
    from .models import Group, User

    schema_factory = SchemaFactory(AlsoChildrenWalker)
    target = _makeOne(schema_factory, Group)

    group = Group(name="ravenclaw", color="blue", created_at=_datetime(2000, 1, 1, 10, 0, 0, 0))
    group.users = [User(name="foo", created_at=_datetime(2000, 1, 1, 10, 0, 0, 0))]

    group_dict = target.dict_from_object(group)
    assert group_dict == {'color': 'blue',
                          'users': [{'created_at': _datetime(2000, 1, 1, 10, 0, 0, 0), 'pk': None, 'name': 'foo'}],
                          'created_at': _datetime(2000, 1, 1, 10, 0, 0, 0),
                          'pk': None,
                          'name': 'ravenclaw'}


def test_it__jsondict_from_model():
    from alchemyjsonschema import AlsoChildrenWalker, SchemaFactory
    from .models import Group, User

    schema_factory = SchemaFactory(AlsoChildrenWalker)
    target = _makeOne(schema_factory, Group)

    group = Group(name="ravenclaw", color="blue", created_at=_datetime(2000, 1, 1, 10, 0, 0, 0))
    group.users = [User(name="foo", created_at=_datetime(2000, 1, 1, 10, 0, 0, 0))]

    jsondict = target.jsondict_from_object(group)

    import json
    assert json.dumps(jsondict)

    assert jsondict == {'color': 'blue',
                        'name': 'ravenclaw',
                        'users': [{'name': 'foo', 'pk': None, 'created_at': '2000-01-01T10:00:00+00:00'}],
                        'pk': None,
                        'created_at': '2000-01-01T10:00:00+00:00'}


def test_it__validate__jsondict():
    from alchemyjsonschema import AlsoChildrenWalker, SchemaFactory
    from .models import Group

    schema_factory = SchemaFactory(AlsoChildrenWalker)
    target = _makeOne(schema_factory, Group)

    jsondict = {'color': 'blue',
                'name': 'ravenclaw',
                'users': [{'name': 'foo', 'pk': None, 'created_at': '2000-01-01T10:00:00+00:00'}],
                'pk': 1,
                'created_at': '2000-01-01T10:00:00+00:00'}

    target.validate_jsondict(jsondict)


def test_it__dict_from_jsondict():
    from alchemyjsonschema import AlsoChildrenWalker, SchemaFactory
    from .models import Group

    schema_factory = SchemaFactory(AlsoChildrenWalker)
    target = _makeOne(schema_factory, Group)

    jsondict = {'color': 'blue',
                'name': 'ravenclaw',
                'users': [{'name': 'foo', 'pk': 10, 'created_at': '2000-01-01T10:00:00+00:00'}],
                'pk': None,
                'created_at': '2000-01-01T10:00:00+00:00'}

    group_dict = target.dict_from_jsondict(jsondict)

    assert group_dict == {'color': 'blue',
                          'users': [{'created_at': _datetime(2000, 1, 1, 10, 0, 0, 0), 'pk': 10, 'name': 'foo'}],
                          'created_at': _datetime(2000, 1, 1, 10, 0, 0, 0),
                          'pk': None,
                          'name': 'ravenclaw'}


def test_it__object_from_dict():
    from alchemyjsonschema import AlsoChildrenWalker, SchemaFactory
    from .models import Group, User

    schema_factory = SchemaFactory(AlsoChildrenWalker)
    target = _makeOne(schema_factory, Group)

    group_dict = {'color': 'blue',
                  'users': [{'created_at': _datetime(2000, 1, 1, 10, 0, 0, 0), 'pk': None, 'name': 'foo'}],
                  'created_at': _datetime(2000, 1, 1, 10, 0, 0, 0),
                  'pk': None,
                  'name': 'ravenclaw'}

    group = target.object_from_dict(group_dict, strict=False)

    assert isinstance(group, Group)
    assert group.color == "blue"
    assert group.name == "ravenclaw"
    assert group.pk is None
    assert group.created_at == _datetime(2000, 1, 1, 10, 0, 0, 0)

    assert (len(group.users) == 1) and (isinstance(group.users[0], User))
    assert group.users[0].name == "foo"
    assert group.users[0].pk is None
    assert group.users[0].created_at == _datetime(2000, 1, 1, 10, 0, 0, 0)

