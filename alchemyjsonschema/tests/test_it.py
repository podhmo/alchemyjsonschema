# -*- coding:utf-8 -*-
def _getTarget():
    from alchemyjsonschema import SchemaFactory
    return SchemaFactory


def _makeOne(*args, **kwargs):
    from alchemyjsonschema import (
        SingleModelWalker,
        DefaultClassfier
    )
    return _getTarget()(SingleModelWalker, DefaultClassfier)


# definition
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Group(Base):
    """model for test"""
    __tablename__ = "Group"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    name = sa.Column(sa.String(255), default="", nullable=False)
    color = sa.Column(sa.Enum("red", "green", "yellow", "blue"))


class User(Base):
    __tablename__ = "User"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    name = sa.Column(sa.String(255), default="", nullable=True)
    group_id = sa.Column(sa.Integer, sa.ForeignKey(Group.pk), nullable=False)
    group = orm.relationship(Group, uselist=False, backref="users")


def test_it_create_schema__and__valid_params__sucess():
    from jsonschema import validate

    target = _makeOne()
    schema = target(Group, excludes=["pk", "users.pk"])
    data = {"name": "ravenclaw", "color": "blue", "users": [{"name": "foo"}, {"name": "bar"}]}

    validate(data, schema)


def test_it_creat_schema__and__invalid_params__failure():
    import pytest
    from jsonschema import validate
    from jsonschema.exceptions import ValidationError

    target = _makeOne()
    schema = target(Group, excludes=["pk", "uesrs.pk"])
    data = {"name": "blackmage", "color": "black", "users": [{"name": "foo"}, {"name": "bar"}]}

    with pytest.raises(ValidationError):
        validate(data, schema)


def test_it2_create_schema__and__valid_params__success():
    from jsonschema import validate

    target = _makeOne()
    schema = target(User, excludes=["pk", "group_id"])
    data = {"name": "foo", "group": {"name": "ravenclaw", "color": "blue", "pk": 1}}
    validate(data, schema)


def test_it_jsonify_data__that_is_valid_params():
    from alchemyjsonschema.dictify import jsonify
    from jsonschema import validate

    target = _makeOne()
    schema = target(User, excludes=["pk", "group_id"])

    user = User(name="foo", group=Group(name="ravenclaw", color="blue", pk=1))
    jsondict = jsonify(user, schema)
    validate(jsondict, schema)
