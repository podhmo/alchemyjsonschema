# -*- coding:utf-8 -*-
def _callFUT(*args, **kwargs):
    from alchemyjsonschema.dictify import dictify
    return dictify(*args, **kwargs)


def _callFUT2(*args, **kwargs):
    from alchemyjsonschema.dictify import normalize
    return normalize(*args, **kwargs)


def _callFUT3(*args, **kwargs):
    from alchemyjsonschema.dictify import prepare
    return prepare(*args, **kwargs)


def _callFUT4(*args, **kwargs):
    from alchemyjsonschema.dictify import jsonify
    return jsonify(*args, **kwargs)


def test_it__dictify():
    from alchemyjsonschema import SchemaFactory, AlsoChildrenWalker
    from alchemyjsonschema.tests.models import Group, User
    from datetime import datetime

    factory = SchemaFactory(AlsoChildrenWalker)
    group_schema = factory(Group)

    created_at = datetime(2000, 1, 1)
    users = [User(name="foo", created_at=created_at),
             User(name="boo", created_at=created_at)]
    group = Group(name="ravenclaw", color="blue", users=users, created_at=created_at)

    result = _callFUT(group, group_schema)
    assert result == {'pk': None, 'color': 'blue', 'name': 'ravenclaw', "created_at": created_at,
                      'users': [{'pk': None, 'name': 'foo', "created_at": created_at},
                                {'pk': None, 'name': 'boo', "created_at": created_at}]}


def test_it__dictify2():
    from alchemyjsonschema import SchemaFactory, AlsoChildrenWalker
    from alchemyjsonschema.tests.models import Group, User
    from datetime import datetime

    factory = SchemaFactory(AlsoChildrenWalker)
    user_schema = factory(User)

    created_at = datetime(2000, 1, 1)
    group = Group(name="ravenclaw", color="blue", created_at=created_at)
    user = User(name="foo", created_at=created_at, group=group)

    result = _callFUT(user, user_schema)
    assert result == {'pk': None, 'name': 'foo', "created_at": created_at,
                      "group": {'pk': None, 'color': 'blue', 'name': 'ravenclaw', "created_at": created_at}}


def test_it__normalize():
    from alchemyjsonschema import SchemaFactory, AlsoChildrenWalker
    from alchemyjsonschema.tests.models import Group
    from datetime import datetime
    import pytz
    created_at = datetime(2000, 1, 1, 0, 0, 0, 0, pytz.utc)

    factory = SchemaFactory(AlsoChildrenWalker)
    group_schema = factory(Group)
    group_dict = {'name': 'ravenclaw', 'created_at': '2000-01-01T00:00:00+00:00', 'color': 'blue', 'pk': None,
                  'users': [{'name': 'foo', 'created_at': '2000-01-01T00:00:00+00:00', 'pk': None},
                            {'name': 'boo', 'created_at': '2000-01-01T00:00:00+00:00', 'pk': None}]}

    result = _callFUT2(group_dict, group_schema)
    assert result == {'pk': None, 'color': 'blue', 'name': 'ravenclaw', "created_at": created_at,
                      'users': [{'pk': None, 'name': 'foo', "created_at": created_at},
                                {'pk': None, 'name': 'boo', "created_at": created_at}]}


def test_it_normalize2():
    from alchemyjsonschema import SchemaFactory, AlsoChildrenWalker
    from alchemyjsonschema.tests.models import User

    factory = SchemaFactory(AlsoChildrenWalker)
    user_schema = factory(User)
    user_dict = {"pk": None, 'name': 'foo', "created_at": None, "group": {"name": "ravenclaw", "color": "blue", "pk": None, "created_at": None}}

    result = _callFUT2(user_dict, user_schema)
    assert result == {"pk": None, 'name': 'foo', "created_at": None, "group": {"name": "ravenclaw", "color": "blue", "pk": None, "created_at": None}}


def test_it_normalize__partial():
    from alchemyjsonschema import SchemaFactory, AlsoChildrenWalker
    from alchemyjsonschema.tests.models import Group

    factory = SchemaFactory(AlsoChildrenWalker)
    group_schema = factory(Group)
    group_dict = {'name': 'ravenclaw', 'color': 'blue'}

    result = _callFUT2(group_dict, group_schema)
    assert result == {'color': 'blue', 'name': 'ravenclaw', 'users': []}


def test_it_normalize__partial2():
    from alchemyjsonschema import SchemaFactory, AlsoChildrenWalker
    from alchemyjsonschema.tests.models import User

    factory = SchemaFactory(AlsoChildrenWalker)
    user_schema = factory(User)
    user_dict = {'name': 'foo'}

    result = _callFUT2(user_dict, user_schema)
    assert result == {'name': 'foo', 'group': None}


def test_it__prepare():
    from alchemyjsonschema import SchemaFactory, AlsoChildrenWalker
    from alchemyjsonschema.tests.models import Group

    factory = SchemaFactory(AlsoChildrenWalker)
    group_schema = factory(Group)
    group_dict = {'name': 'ravenclaw', 'created_at': '2000-01-01T00:00:00+00:00', 'color': 'blue', 'pk': 1,
                  'users': [{'name': 'foo', 'created_at': '2000-01-01T00:00:00+00:00', 'pk': 12},
                            {'name': 'boo', 'created_at': '2000-01-01T00:00:00+00:00', 'pk': 13}]}

    result = _callFUT3(group_dict, group_schema)
    assert result == {'name': 'ravenclaw', 'created_at': '2000-01-01T00:00:00+00:00',
                      'color': 'blue', 'pk': 1,
                      'users': [{'name': 'foo', 'created_at': '2000-01-01T00:00:00+00:00', 'pk': 12},
                                {'name': 'boo', 'created_at': '2000-01-01T00:00:00+00:00', 'pk': 13}]}


def test_it__prepare_partial():
    from alchemyjsonschema import SchemaFactory, AlsoChildrenWalker
    from alchemyjsonschema.tests.models import Group

    factory = SchemaFactory(AlsoChildrenWalker)
    group_schema = factory(Group)
    group_dict = {'name': 'ravenclaw', 'color': 'blue', 'pk': 1}

    result = _callFUT3(group_dict, group_schema)
    assert result == {'name': 'ravenclaw', 'pk': 1, 'color': 'blue', 'users': []}


def test_it__jsonify():
    from alchemyjsonschema import SchemaFactory, AlsoChildrenWalker
    from alchemyjsonschema.tests.models import Group, User
    from datetime import datetime

    factory = SchemaFactory(AlsoChildrenWalker)
    group_schema = factory(Group)

    created_at = datetime(2000, 1, 1)
    users = [User(name="foo", created_at=created_at),
             User(name="boo", created_at=created_at)]
    group = Group(name="ravenclaw", color="blue", users=users, created_at=created_at)

    result = _callFUT4(group, group_schema)
    assert result == {'name': 'ravenclaw', 'created_at': '2000-01-01T00:00:00+00:00', 'color': 'blue', 'pk': None,
                      'users': [{'name': 'foo', 'created_at': '2000-01-01T00:00:00+00:00', 'pk': None},
                                {'name': 'boo', 'created_at': '2000-01-01T00:00:00+00:00', 'pk': None}]}

