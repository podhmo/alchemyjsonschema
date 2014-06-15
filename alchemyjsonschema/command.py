# -*- coding:utf-8 -*-
import sys
import pkg_resources
import json
import argparse


from . import (
    SchemaFactory,
    AlsoChildrenWalker,
    OneModelOnlyWalker,
    SingleModelWalker,
    HandControlledWalkerFactory,
    RelationDesicion,
    ComfortableDesicion
)


def import_symbol(symbol):  # todo cache
    return pkg_resources.EntryPoint.parse("x=%s" % symbol).load(False)


def err(x):
    sys.stderr.write(x)
    sys.stderr.write("\n")
    sys.stderr.flush()


def detect_walker(x):
    if x == "structual":
        return AlsoChildrenWalker
    elif x == "noforeignkey":
        return OneModelOnlyWalker
    elif x == "foreignkey":
        return SingleModelWalker
    elif x == "control":
        return HandControlledWalkerFactory
    else:
        raise Exception(x)


def detect_decision(x):
    if x == "default":
        return RelationDesicion()
    elif x == "comfortable":
        return ComfortableDesicion()
    else:
        raise Exception(x)


def run(model, walker, depth=None, relation_decision=None):
    make_schema = SchemaFactory(walker, relation_decision=relation_decision)
    schema = make_schema(model, depth=depth)
    print(json.dumps(schema, indent=2, ensure_ascii=False))


def main(sys_args=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument("model")
    parser.add_argument("--walker", choices=["noforeignkey", "foreignkey", "structual", "control"], default="structual")
    parser.add_argument("--decision", choices=["default", "comfortable"], default="default")
    parser.add_argument("--depth", default=None, type=int)
    parser.add_argument("--decision-relationship", default="")
    parser.add_argument("--decision-foreignkey", default="")
    args = parser.parse_args(sys_args)
    walker = detect_walker(args.walker)
    model = import_symbol(args.model)
    if walker == HandControlledWalkerFactory:
        decisions = {k.strip(): "relationship" for k in args.decision_relationship.split(" ")}
        decisions.update({k.strip(): "foreignkey" for k in args.decision_foreignkey.split(" ")})
        walker = walker(decisions)
    return run(model, walker, depth=args.depth, relation_decision=detect_decision(args.decision))
