#!/usr/bin/env python3
"""Read-only e-Gov Law API v2 client; uses only the Python standard library."""

import argparse
from datetime import date
import json
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://laws.e-gov.go.jp/api/2"


def nonempty(value):
    value = value.strip()
    if not value:
        raise argparse.ArgumentTypeError("空の検索語・法令IDは指定できません。")
    return value


def limit_value(value):
    value = int(value)
    if not 1 <= value <= 50:
        raise argparse.ArgumentTypeError("limitは1〜50を指定してください。")
    return value


def offset_value(value):
    value = int(value)
    if value < 0:
        raise argparse.ArgumentTypeError("offsetは0以上を指定してください。")
    return value


def iso_date(value):
    try:
        if date.fromisoformat(value).isoformat() != value:
            raise ValueError
    except ValueError:
        raise argparse.ArgumentTypeError("日付はYYYY-MM-DD形式で指定してください。")
    return value


def make_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    search = commands.add_parser("search", help="キーワードから法令候補を検索")
    search.add_argument("keyword", type=nonempty)
    search.add_argument("--title", action="store_true", help="本文ではなく法令名で検索")
    search.add_argument("--limit", type=limit_value, default=10)
    search.add_argument("--offset", type=offset_value, default=0)
    search.add_argument("--asof", type=iso_date)
    law = commands.add_parser("law", help="法令ID・番号・履歴IDから条文を取得")
    law.add_argument("id", type=nonempty)
    law.add_argument("--asof", type=iso_date)
    law.add_argument("--elm", type=nonempty, help="取得する条項（例: MainProvision-Article[1]）")
    revisions = commands.add_parser("revisions", help="法令ID・番号から改正履歴を取得")
    revisions.add_argument("id", type=nonempty)
    for command in (search, law, revisions):
        command.add_argument("--output", type=Path, help="結果をUTF-8のJSONファイルへ保存")
    return parser


def build_url(args):
    query = {"response_format": "json"}
    if args.command == "search":
        path = "/laws" if args.title else "/keyword"
        query["law_title" if args.title else "keyword"] = args.keyword
        query.update(limit=args.limit, offset=args.offset)
        if args.asof:
            query["asof"] = args.asof
    elif args.command == "law":
        path = "/law_data/" + quote(args.id, safe="")
        query["law_full_text_format"] = "json"
        if args.asof:
            query["asof"] = args.asof
        if args.elm:
            query["elm"] = args.elm
    else:
        path = "/law_revisions/" + quote(args.id, safe="")
    return BASE_URL + path + "?" + urlencode(query)


def fetch(args):
    request = Request(
        build_url(args),
        headers={"Accept": "application/json", "User-Agent": "Sharaku-Mrs-Legal-Advisor/0.1.0"},
    )
    with urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError("APIの応答がJSONオブジェクトではありません。")
    expected = (
        ("laws" if args.title else "items")
        if args.command == "search"
        else ("law_full_text" if args.command == "law" else "revisions")
    )
    if expected not in payload:
        raise ValueError("API応答に必要なフィールドがありません: " + expected)
    return payload


def main(argv=None):
    args = make_parser().parse_args(argv)
    try:
        payload = fetch(args)
        text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(text, encoding="utf-8")
            print(str(args.output.resolve()))
        else:
            print(text, end="")
    except HTTPError as error:
        detail = error.read(4096).decode("utf-8", errors="replace")
        print(f"e-Gov API HTTP {error.code}: {detail}", file=sys.stderr)
        return 1
    except (URLError, TimeoutError, OSError, ValueError) as error:
        print(f"e-Gov APIの取得・保存に失敗しました: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
