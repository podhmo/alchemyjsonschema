import argparse
from magicalimport import import_symbol


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="the module or class to extract schemas from")
    parser.add_argument("--format", default=None, choices=["json", "yaml"])
    parser.add_argument(
        "--walker",
        choices=["noforeignkey", "foreignkey", "structural"],
        default="structural",
    )
    parser.add_argument(
        "--decision", choices=["default", "useforeignkey"], default="default"
    )
    parser.add_argument("--depth", default=None, type=int)
    parser.add_argument("--out", default=None, help="output to file")
    parser.add_argument(
        "--layout",
        choices=["swagger2.0", "jsonschema", "openapi3.0", "openapi2.0"],
        default="swagger2.0",
    )
    parser.add_argument("--driver", default="alchemyjsonschema.command.driver:Driver")
    args = parser.parse_args()

    driver_cls = import_symbol(args.driver)
    driver = driver_cls(args.walker, args.decision, args.layout)
    driver.run(args.target, args.out, format=args.format)
