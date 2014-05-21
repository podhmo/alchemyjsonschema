# -*- coding:utf-8 -*-
def _callFUT(*args, **kwargs):
    from alchemyjsonschema.dictify import dictify
    return dictify(*args, **kwargs)


def test_it():
    from alchemyjsonschema import SchemaFactory, AlsoChildrenWalker
    from alchemyjsonschema.tests.models import Group, User

    factory = SchemaFactory(AlsoChildrenWalker)
    group_schema = factory.create(Group)

    users = [User(name="foo"), User(name="boo")]
    group = Group(name="ravenclaw", color="blue", users=users)

    result = _callFUT(group, group_schema)
    assert result == {'pk': None, 'color': 'blue', 'name': 'ravenclaw',
                      'users': [{'pk': None, 'name': 'foo'}, {'pk': None, 'name': 'boo'}]}
