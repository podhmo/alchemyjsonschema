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


## definition
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Group(Base):
    """model for test"""
    __tablename__ = "Group"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    name = sa.Column(sa.String(255), default="", nullable=False)

class User(Base):
    __tablename__ = "User"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    name = sa.Column(sa.String(255), default="", nullable=True)
    group_id = sa.Column(sa.Integer, sa.ForeignKey(Group.pk), nullable=False)
    group = orm.relationship(Group, uselist=False, backref="users")


def test_properties():
    target = _makeOne()
    result = target.create(User)

    assert "properties" in result
    assert list(sorted(result["properties"].keys())) == ["group_id", "name", "pk"]

def test_required__are_foreignKey_and_nullable_is_false():
    target = _makeOne()
    result = target.create(User)

    assert "required" in result
    assert list(sorted(result["required"])) == ["group_id", "pk"]
