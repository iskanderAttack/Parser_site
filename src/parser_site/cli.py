"""Command line interface for parser_site."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .parser import ParseResult, parse_contacts

_FIELDS = ("emails", "urls", "phones")


class CliInputError(ValueError):
    """Raised when CLI input is invalid or unavailable."""


def _read_input_text(args: argparse.Namespace) -> str:
    if args.file and args.text:
        raise CliInputError("Use either positional text or --file, not both")

    if args.file:
        try:
            return Path(args.file).read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            raise CliInputError(f"Input file not found: {args.file}") from exc
        except OSError as exc:
            raise CliInputError(f"Failed to read input file: {args.file}") from exc

    if args.text:
        return args.text

    if not sys.stdin.isatty():
        return sys.stdin.read()

    raise CliInputError("Provide text argument, --file, or pipe input via stdin")


def _build_payload(result: ParseResult, only: list[str] | None) -> dict[str, list[str]]:
    payload = {"emails": result.emails, "urls": result.urls, "phones": result.phones}
    if not only:
        return payload

    selected = set(only)
    ordered_only = [field for field in _FIELDS if field in selected]
    return {field: payload[field] for field in ordered_only}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract emails, URLs and phone numbers from text"
    )
    parser.add_argument("text", nargs="?", help="Input text to parse")
    parser.add_argument("--file", "-f", help="Read input text from a UTF-8 file")
    parser.add_argument(
        "--only",
        action="append",
        choices=_FIELDS,
        help="Include only selected field(s); can be repeated",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    try:
        args = parser.parse_args(argv)
        text = _read_input_text(args)
        if not text.strip():
            raise CliInputError("Input text is empty")

        result = parse_contacts(text)
        payload = _build_payload(result, args.only)

        if args.pretty:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(payload, ensure_ascii=False))
        return 0
    except CliInputError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
