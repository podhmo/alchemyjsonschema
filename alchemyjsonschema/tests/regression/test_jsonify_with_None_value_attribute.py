# -*- coding:utf-8 -*-
import pytest


def _callFUT(*args, **kwargs):
    # see: https://github.com/podhmo/alchemyjsonschema/pull/3
    from alchemyjsonschema.dictify import jsonify
    return jsonify(*args, **kwargs)


def _makeSchema(model):
    from alchemyjsonschema import SchemaFactory, AlsoChildrenWalker
    factory = SchemaFactory(AlsoChildrenWalker)
    return factory(model)


def _makeModel():
    import sqlalchemy as sa
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()

    class UserKey(Base):
        __tablename__ = "user_key"
        key = sa.Column(sa.Integer, sa.Sequence('user_id_seq'), primary_key=True, doc="primary key")
        deactivated_at = sa.Column(sa.DateTime(), nullable=True)
        keytype = sa.Column(sa.String(36), nullable=False)

    return UserKey


def test_it():
    UserKey = _makeModel()
    schema = _makeSchema(UserKey)

    uk = UserKey(key=1, keytype="*keytype*")
    d = _callFUT(uk, schema)

    assert "deactivated_at" not in d

    import jsonschema
    jsonschema.validate(d, schema)


def test_it__validation_failure__when_verbose_is_True():
    UserKey = _makeModel()
    schema = _makeSchema(UserKey)

    uk = UserKey(key=1, keytype="*keytype*")
    d = _callFUT(uk, schema, verbose=True)

    assert d["deactivated_at"] is None

    import jsonschema
    from jsonschema.exceptions import ValidationError

    with pytest.raises(ValidationError):
        jsonschema.validate(d, schema)
