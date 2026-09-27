from __future__ import annotations

import argparse
import json
import sys


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="goldfish", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("serve", help="run the goldfish MCP server (stdio)")
    sub.add_parser("status", help="print health across all three memory tiers")

    remember_p = sub.add_parser("remember", help="write a curated memory note")
    remember_p.add_argument("name")
    remember_p.add_argument("description")
    remember_p.add_argument("--type", choices=("user", "feedback", "project", "reference"), required=True)
    remember_p.add_argument("--content", required=True, help="note body (markdown)")

    recall_p = sub.add_parser("recall", help="read or search curated memory notes")
    recall_p.add_argument("name", nargs="?")
    recall_p.add_argument("--query")
    recall_p.add_argument("--type", choices=("user", "feedback", "project", "reference"))

    args = parser.parse_args(argv)

    if args.command == "serve":
        from .server import main as serve_main
        serve_main()
        return

    if args.command == "status":
        from .server import goldfish_status
        print(json.dumps(goldfish_status(), indent=2, default=str))
        return

    if args.command == "remember":
        from .server import goldfish_remember
        print(json.dumps(goldfish_remember(args.name, args.description, args.type, args.content), indent=2))
        return

    if args.command == "recall":
        from .server import goldfish_recall
        print(json.dumps(goldfish_recall(name=args.name, query=args.query, type=args.type), indent=2))
        return

    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
