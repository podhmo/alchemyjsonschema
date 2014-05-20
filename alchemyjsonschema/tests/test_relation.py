# -*- coding:utf-8 -*-
def _getTarget():
    from alchemyjsonschema import SchemaFactory
    return SchemaFactory

def _makeOne(walker):
    from alchemyjsonschema import DefaultClassfier
    return _getTarget()(walker, DefaultClassfier)


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


def test_properties__default__includes__foreign_keys():
    from alchemyjsonschema import SingleModelWalker
    target = _makeOne(SingleModelWalker)
    result = target.create(User)

    assert "properties" in result
    assert list(sorted(result["properties"].keys())) == ["group_id", "name", "pk"]

def test_required__are_foreignKey_and_nullable_is_false():
    from alchemyjsonschema import SingleModelWalker
    target = _makeOne(SingleModelWalker)
    result = target.create(User)

    assert "required" in result
    assert list(sorted(result["required"])) == ["group_id", "pk"]

def test_properties__only_onesself__not_includes__foreign_keys():
    from alchemyjsonschema import OneModelOnlyWalker
    target = _makeOne(OneModelOnlyWalker)
    result = target.create(User)

    assert "required" in result
    assert list(sorted(result["properties"])) == ["name", "pk"]
