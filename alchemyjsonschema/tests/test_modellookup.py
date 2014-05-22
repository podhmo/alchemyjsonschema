# -*- coding:utf-8 -*-
def _getTarget():
    from alchemyjsonschema.dictify import ModelLookup
    return ModelLookup


def _makeOne(*args, **kwargs):
    return _getTarget()(*args, **kwargs)


def test_root_model():
    import alchemyjsonschema.tests.models as models
    from alchemyjsonschema.tests.models import Group
    target = _makeOne(models)
    result = target("Group")
    assert result == Group


def test_child__of__root_model():
    import alchemyjsonschema.tests.models as models
    from alchemyjsonschema.tests.models import User
    """
    Group.users -> [User]
    """
    target = _makeOne(models)
    target("Group")
    result = target("users")
    assert result == User


def test_child__of__child__of__root_model():
    import alchemyjsonschema.tests.models as models
    from alchemyjsonschema.tests.models import Group
    """
    Group.users -> [User]
    User.group -> Group
    """
    target = _makeOne(models)
    target("Group")
    target("users")
    result = target("group")
    assert result == Group
