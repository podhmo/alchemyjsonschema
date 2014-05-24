# -*- coding:utf-8 -*-
def _getTarget():
    from alchemyjsonschema import SchemaFactory
    return SchemaFactory


def _makeOne(walker):
    from alchemyjsonschema import DefaultClassfier
    return _getTarget()(walker, DefaultClassfier)


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


class User(Base):
    __tablename__ = "User"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")
    name = sa.Column(sa.String(255), default="", nullable=True)
    group_id = sa.Column(sa.Integer, sa.ForeignKey(Group.pk), nullable=False)
    group = orm.relationship(Group, uselist=False, backref="users")


def test_properties__default__includes__foreign_keys():
    from alchemyjsonschema import SingleModelWalker
    target = _makeOne(SingleModelWalker)
    result = target(User)

    assert "properties" in result
    assert list(sorted(result["properties"].keys())) == ["group_id", "name", "pk"]


def test_required__are_foreignKey_and_nullable_is_false():
    from alchemyjsonschema import SingleModelWalker
    target = _makeOne(SingleModelWalker)
    result = target(User)

    assert "required" in result
    assert list(sorted(result["required"])) == ["group_id", "pk"]


def test_properties__only_onesself__not_includes__foreign_keys():
    from alchemyjsonschema import OneModelOnlyWalker
    target = _makeOne(OneModelOnlyWalker)
    result = target(User)

    assert "required" in result
    assert list(sorted(result["properties"])) == ["name", "pk"]


def test_properties__include_OnetoMany_relation():
    from alchemyjsonschema import AlsoChildrenWalker
    target = _makeOne(AlsoChildrenWalker)
    result = target(User)

    assert "required" in result
    assert list(sorted(result["properties"])) == ["group", "name", "pk"]
    assert result["properties"]["group"] == {'name': {'maxLength': 255, 'type': 'string'},
                                             'pk': {'description': 'primary key', 'type': 'integer'}}


def test_properties__include_ManytoOne_backref():
    from alchemyjsonschema import AlsoChildrenWalker
    target = _makeOne(AlsoChildrenWalker)
    result = target(Group)

    assert "required" in result
    assert list(sorted(result["properties"])) == ["name", "pk", "users"]
    assert result["properties"]["users"] == {"type": "array",
                                             "items": {'name': {'maxLength': 255, 'type': 'string'},
                                                       'pk': {'description': 'primary key', 'type': 'integer'}}}


# depth
class A0(Base):
    __tablename__ = "A0"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key")


class A1(Base):
    __tablename__ = "A1"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key1")
    parent_id = sa.Column(sa.Integer, sa.ForeignKey(A0.pk), nullable=False)
    parent = orm.relationship(A0, uselist=False, backref="children")


class A2(Base):
    __tablename__ = "A2"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key2")
    parent_id = sa.Column(sa.Integer, sa.ForeignKey(A1.pk), nullable=False)
    parent = orm.relationship(A1, uselist=False, backref="children")


class A3(Base):
    __tablename__ = "A3"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key3")
    parent_id = sa.Column(sa.Integer, sa.ForeignKey(A2.pk), nullable=False)
    parent = orm.relationship(A2, uselist=False, backref="children")


class A4(Base):
    __tablename__ = "A4"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key4")
    parent_id = sa.Column(sa.Integer, sa.ForeignKey(A3.pk), nullable=False)
    parent = orm.relationship(A3, uselist=False, backref="children")


class A5(Base):
    __tablename__ = "A5"

    pk = sa.Column(sa.Integer, primary_key=True, doc="primary key5")
    parent_id = sa.Column(sa.Integer, sa.ForeignKey(A4.pk), nullable=False)
    parent = orm.relationship(A4, uselist=False, backref="children")


def test_properties__default_depth_is__traverse_all_chlidren():
    from alchemyjsonschema import AlsoChildrenWalker
    target = _makeOne(AlsoChildrenWalker)
    result = target(A0)

    assert "required" in result
    assert list(sorted(result["properties"])) == ["children", "pk"]
    assert (result["properties"]
            ["children"]["items"]["children"]["items"]["children"]["items"]["children"]["items"]["children"]["items"]
            ["pk"]["description"] == "primary key5")


def test_properties__default_depth_is__2__traverse_depth2():
    from alchemyjsonschema import AlsoChildrenWalker
    target = _makeOne(AlsoChildrenWalker)
    result = target(A0, depth=2)

    assert "required" in result
    assert list(sorted(result["properties"])) == ["children", "pk"]
    assert (result["properties"]
            ["children"]["items"]
            ["pk"]["description"] == "primary key1")


def test_properties__default_depth_is__3__traverse_depth3():
    from alchemyjsonschema import AlsoChildrenWalker
    target = _makeOne(AlsoChildrenWalker)
    result = target(A0, depth=3)

    assert "required" in result
    assert list(sorted(result["properties"])) == ["children", "pk"]
    assert (result["properties"]
            ["children"]["items"]["children"]["items"]
            ["pk"]["description"] == "primary key2")
