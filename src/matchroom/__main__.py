"""Command line: generate a synthetic match, or build a recap from one."""

from __future__ import annotations

import argparse
import json
import sys

from .generator import generate_match
from .pipeline import build_recap
from .schema import Match


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="matchroom")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="generate a synthetic match")
    gen.add_argument("--seed", type=int, default=7)
    gen.add_argument("--out", default="-", help="output path, or - for stdout")

    rec = sub.add_parser("recap", help="build a verified recap from a match file")
    rec.add_argument("match_file")
    rec.add_argument("--audience", choices=["fan", "analyst"], default="fan")
    rec.add_argument("--json", action="store_true", help="print the full structured recap")

    args = parser.parse_args(argv)

    if args.command == "generate":
        payload = json.dumps(generate_match(args.seed).to_dict(), indent=1)
        if args.out == "-":
            print(payload)
        else:
            with open(args.out, "w") as fh:
                fh.write(payload + "\n")
            print(f"wrote {args.out}", file=sys.stderr)
        return 0

    with open(args.match_file) as fh:
        match = Match.from_dict(json.load(fh))
    recap = build_recap(match, args.audience)
    print(json.dumps(recap, indent=2) if args.json else recap["text"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
