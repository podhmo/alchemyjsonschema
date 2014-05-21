# -*- coding:utf-8 -*-
def _callFUT(*args, **kwargs):
    from alchemyjsonschema.dictify import dictify
    return dictify(*args, **kwargs)


def test_it__dictify():
    from alchemyjsonschema import SchemaFactory, AlsoChildrenWalker
    from alchemyjsonschema.tests.models import Group, User
    from datetime import datetime

    factory = SchemaFactory(AlsoChildrenWalker)
    group_schema = factory.create(Group)

    created_at = datetime(2000, 1, 1)
    users = [User(name="foo", created_at=created_at),
             User(name="boo", created_at=created_at)]
    group = Group(name="ravenclaw", color="blue", users=users, created_at=created_at)

    result = _callFUT(group, group_schema)
    assert result == {'pk': None, 'color': 'blue', 'name': 'ravenclaw', "created_at": created_at,
                      'users': [{'pk': None, 'name': 'foo', "created_at": created_at},
                                {'pk': None, 'name': 'boo', "created_at": created_at}]}


def test_it__jsonify():
    from alchemyjsonschema import SchemaFactory, AlsoChildrenWalker
    from alchemyjsonschema.tests.models import Group, User
    from datetime import datetime
    from alchemyjsonschema.dictify import converted_of

    factory = SchemaFactory(AlsoChildrenWalker)
    group_schema = factory.create(Group)

    created_at = datetime(2000, 1, 1)
    users = [User(name="foo", created_at=created_at),
             User(name="boo", created_at=created_at)]
    group = Group(name="ravenclaw", color="blue", users=users, created_at=created_at)

    result = _callFUT(group, group_schema, getter=converted_of)
    assert result == {'name': 'ravenclaw', 'created_at': '2000-01-01T00:00:00', 'color': 'blue', 'pk': None,
                      'users': [{'name': 'foo', 'created_at': '2000-01-01T00:00:00', 'pk': None},
                                {'name': 'boo', 'created_at': '2000-01-01T00:00:00', 'pk': None}]}
