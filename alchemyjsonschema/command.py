# -*- coding:utf-8 -*-
import sys
import pkg_resources
import json
import argparse


from . import (
    SchemaFactory,
    AlsoChildrenWalker,
    OneModelOnlyWalker,
    SingleModelWalker
)


def import_symbol(symbol):  # todo cache
    return pkg_resources.EntryPoint.parse("x=%s" % symbol).load(False)


def err(x):
    sys.stderr.write(x)
    sys.stderr.write("\n")
    sys.stderr.flush()


def detect_walker(x):
    if x == "alsochildren":
        return AlsoChildrenWalker
    elif x == "onlyone":
        return OneModelOnlyWalker
    elif x == "single":
        return SingleModelWalker
    else:
        raise Exception(x)


def run(args):
    model = import_symbol(args.model)
    walker = detect_walker(args.walker)
    make_schema = SchemaFactory(walker)
    schema = make_schema(model)
    print(json.dumps(schema, indent=2, ensure_ascii=False))


def main(sys_args=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("program")
    parser.add_argument("model")
    parser.add_argument("--walker", choices=["onlyone", "single", "alsochildren"], default="alsochildren")
    args = parser.parse_args(sys_args)
    return run(args)
