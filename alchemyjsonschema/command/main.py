import argparse
from magicalimport import import_symbol
from alchemyjsonschema import (
    StructuralWalker,
    NoForeignKeyWalker,
    ForeignKeyWalker,
)
from alchemyjsonschema import (
    RelationDesicion,
    UseForeignKeyIfPossibleDecision,
)


def detect_walker(x):
    if x == "structural":
        return StructuralWalker
    elif x == "noforeignkey":
        return NoForeignKeyWalker
    elif x == "foreignkey":
        return ForeignKeyWalker
    else:
        raise ValueError(x)


def detect_decision(x):
    if x == "default":
        return RelationDesicion()
    elif x == "useforeignkey":
        return UseForeignKeyIfPossibleDecision()
    else:
        raise ValueError(x)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help='the module or class to extract schemas from')
    parser.add_argument("--format", default="json", choices=["json", "yaml"])
    parser.add_argument(
        "--walker", choices=["noforeignkey", "foreignkey", "structural"], default="structural"
    )
    parser.add_argument("--decision", choices=["default", "useforeignkey"], default="default")
    parser.add_argument("--depth", default=None, type=int)
    parser.add_argument("--out", default=None, help='output to file')
    parser.add_argument("--layout", choices=["swagger2.0", "jsonschema"])
    parser.add_argument("--driver", default="alchemyjsonschema.command.driver:Driver")
    args = parser.parse_args()

    walker = detect_walker(args.walker)
    relation_decision = detect_decision(args.decision)
    driver_cls = import_symbol(args.driver)
    driver = driver_cls(walker, relation_decision, args.format)
    driver.run(args.target, args.out)
