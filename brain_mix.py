#!/usr/bin/env python3
"""Offline Brain Mix CLI.

Single-file utility that mixes:
1) Agent/subagent catalog browsing
2) Skill catalog browsing
3) Practical offline commands for local work

No third-party dependencies required (Python stdlib only).
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import os
import platform
import re
import shlex
import sys
from pathlib import Path
from typing import Iterable

SUBAGENTS = sorted(
    {
        "API Readiness Analyzer",
        "ai-architect",
        "best-of-n-runner",
        "convex-advisor",
        "convex-reviewer",
        "cursor-guide",
        "deployment-expert",
        "encore-assistant",
        "explore",
        "generalPurpose",
        "performance-optimizer",
        "render-assistant",
        "security-review",
        "test-case-generator",
        "bugbot",
    },
    key=str.lower,
)

MODES = sorted({"agent", "ask", "debug", "plan"}, key=str.lower)

SKILLS = sorted(
    {
        "agent-ready-apis",
        "agents-sdk",
        "ai-gateway",
        "ai-sdk",
        "amazon-location-service",
        "amplify-workflow",
        "api-gateway",
        "atlas-stream-processing",
        "auth",
        "auth-setup",
        "aws-lambda",
        "aws-lambda-durable-functions",
        "aws-lambda-managed-instances",
        "aws-serverless-deployment",
        "aws-step-functions",
        "bootstrap",
        "building-ai-agent-on-cloudflare",
        "building-mcp-server-on-cloudflare",
        "chat-sdk",
        "clerk",
        "clerk-android",
        "clerk-astro-patterns",
        "clerk-backend-api",
        "clerk-billing",
        "clerk-chrome-extension-patterns",
        "clerk-custom-ui",
        "clerk-expo",
        "clerk-expo-patterns",
        "clerk-nextjs-patterns",
        "clerk-nuxt-patterns",
        "clerk-orgs",
        "clerk-react-patterns",
        "clerk-react-router-patterns",
        "clerk-setup",
        "clerk-swift",
        "clerk-tanstack-patterns",
        "clerk-testing",
        "clerk-vue-patterns",
        "clerk-webhooks",
        "cloudflare",
        "components-guide",
        "convex-helpers-guide",
        "convex-quickstart",
        "databricks-apps",
        "databricks-core",
        "databricks-dabs",
        "databricks-jobs",
        "databricks-lakebase",
        "databricks-model-serving",
        "databricks-pipelines",
        "databricks-serverless-migration",
        "databricks-vector-search",
        "ddconfig",
        "ddsetup",
        "ddtoolsets",
        "deployments-cicd",
        "durable-objects",
        "env-vars",
        "figma-code-connect",
        "figma-create-new-file",
        "figma-generate-design",
        "figma-generate-diagram",
        "figma-generate-library",
        "figma-swiftui",
        "figma-use",
        "figma-use-figjam",
        "figma-use-slides",
        "firebase-ai-logic-basics",
        "firebase-app-hosting-basics",
        "firebase-auth-basics",
        "firebase-basics",
        "function-creator",
        "knowledge-update",
        "marketplace",
        "migration-helper",
        "mongodb-connection",
        "mongodb-mcp-setup",
        "mongodb-natural-language-querying",
        "mongodb-query-optimizer",
        "mongodb-schema-design",
        "mongodb-search-and-ai",
        "next-cache-components",
        "next-forge",
        "next-upgrade",
        "nextjs",
        "postman-knowledge",
        "postman-routing",
        "react-best-practices",
        "render-background-workers",
        "render-blueprints",
        "render-cli",
        "render-cron-jobs",
        "render-debug",
        "render-deploy",
        "render-disks",
        "render-docker",
        "render-domains",
        "render-env-vars",
        "render-keyvalue",
        "render-mcp",
        "render-migrate-from-heroku",
        "render-monitor",
        "render-networking",
        "render-postgres",
        "render-private-services",
        "render-scaling",
        "render-static-sites",
        "render-web-services",
        "render-workflows",
        "routing-middleware",
        "run-mobile-tests-on-browserstack",
        "run-web-tests-on-browserstack",
        "runtime-cache",
        "sandbox-sdk",
        "scan-and-fix-accessibility",
        "schema-builder",
        "sentry-feature-setup",
        "sentry-sdk-setup",
        "sentry-workflow",
        "shadcn",
        "supabase",
        "supabase-postgres-best-practices",
        "turbopack",
        "vercel-agent",
        "vercel-cli",
        "vercel-functions",
        "vercel-sandbox",
        "vercel-storage",
        "verification",
        "web-perf",
        "workflow",
        "workers-best-practices",
        "wrangler",
    },
    key=str.lower,
)


def print_section(title: str, values: Iterable[str]) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    for index, item in enumerate(values, start=1):
        print(f"{index:>3}. {item}")


def cmd_catalog(_: argparse.Namespace) -> int:
    print_section("Subagents", SUBAGENTS)
    print_section("Modes", MODES)
    print_section("Skills", SKILLS)
    return 0


def cmd_ls(args: argparse.Namespace) -> int:
    target = Path(args.path).expanduser()
    if not target.exists():
        print(f"Path not found: {target}", file=sys.stderr)
        return 1
    if target.is_file():
        print(target)
        return 0

    entries = sorted(target.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    for entry in entries:
        kind = "DIR " if entry.is_dir() else "FILE"
        print(f"{kind}  {entry}")
    return 0


def cmd_sysinfo(_: argparse.Namespace) -> int:
    now = dt.datetime.now().astimezone()
    print(f"Time: {now.isoformat()}")
    print(f"Platform: {platform.platform()}")
    print(f"Python: {platform.python_version()}")
    print(f"Hostname: {platform.node()}")
    print(f"Working directory: {Path.cwd()}")
    return 0


def cmd_hash(args: argparse.Namespace) -> int:
    file_path = Path(args.file).expanduser()
    if not file_path.exists() or not file_path.is_file():
        print(f"File not found: {file_path}", file=sys.stderr)
        return 1

    algorithm = args.algorithm.lower()
    if algorithm not in {"sha256", "sha1", "md5"}:
        print("Unsupported algorithm. Use: sha256, sha1, md5", file=sys.stderr)
        return 1

    hasher = hashlib.new(algorithm)
    with file_path.open("rb") as handle:
        while True:
            chunk = handle.read(8192)
            if not chunk:
                break
            hasher.update(chunk)
    print(f"{algorithm}  {hasher.hexdigest()}  {file_path}")
    return 0


def cmd_read(args: argparse.Namespace) -> int:
    file_path = Path(args.file).expanduser()
    if not file_path.exists() or not file_path.is_file():
        print(f"File not found: {file_path}", file=sys.stderr)
        return 1

    try:
        with file_path.open("r", encoding="utf-8", errors="replace") as handle:
            for number, line in enumerate(handle, start=1):
                if number > args.max_lines:
                    print(f"... (truncated after {args.max_lines} lines)")
                    break
                print(f"{number:>4}: {line.rstrip()}")
    except OSError as exc:
        print(f"Read failed: {exc}", file=sys.stderr)
        return 1
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    root = Path(args.path).expanduser()
    if not root.exists():
        print(f"Path not found: {root}", file=sys.stderr)
        return 1

    try:
        pattern = re.compile(args.pattern, re.IGNORECASE if args.ignore_case else 0)
    except re.error as exc:
        print(f"Invalid regex pattern: {exc}", file=sys.stderr)
        return 1

    extensions = tuple(args.ext or [])
    max_hits = max(args.max_hits, 1)
    hits = 0

    candidates: list[Path]
    if root.is_file():
        candidates = [root]
    else:
        candidates = [p for p in root.rglob("*") if p.is_file()]

    for file_path in sorted(candidates, key=lambda p: str(p).lower()):
        if extensions and not file_path.suffix.lower().lstrip(".") in extensions:
            continue
        try:
            with file_path.open("r", encoding="utf-8", errors="ignore") as handle:
                for line_number, line in enumerate(handle, start=1):
                    if pattern.search(line):
                        print(f"{file_path}:{line_number}: {line.rstrip()}")
                        hits += 1
                        if hits >= max_hits:
                            print(f"\nReached max hits: {max_hits}")
                            return 0
        except OSError:
            continue

    if hits == 0:
        print("No matches.")
    return 0


def cmd_repl(_: argparse.Namespace) -> int:
    print("Offline Brain Mix REPL")
    print("Type 'help' for commands, 'exit' to quit.\n")
    while True:
        try:
            raw = input("brain> ").strip()
        except EOFError:
            print()
            return 0
        except KeyboardInterrupt:
            print("\nInterrupted.")
            return 0

        if not raw:
            continue
        if raw in {"exit", "quit"}:
            return 0
        if raw == "help":
            print(
                "Commands:\n"
                "  catalog                    Show subagents, modes, skills\n"
                "  sysinfo                    Show local system info\n"
                "  ls [path]                  List directory entries\n"
                "  read <file> [max_lines]    Print file preview\n"
                "  hash <file> [algorithm]    Hash file: sha256|sha1|md5\n"
                "  search <regex> [path]      Regex search local files\n"
                "  exit                        Quit REPL"
            )
            continue

        parts = shlex.split(raw)
        command = parts[0]
        try:
            if command == "catalog":
                cmd_catalog(argparse.Namespace())
            elif command == "sysinfo":
                cmd_sysinfo(argparse.Namespace())
            elif command == "ls":
                target = parts[1] if len(parts) > 1 else "."
                cmd_ls(argparse.Namespace(path=target))
            elif command == "read":
                if len(parts) < 2:
                    print("Usage: read <file> [max_lines]")
                    continue
                max_lines = int(parts[2]) if len(parts) > 2 else 80
                cmd_read(argparse.Namespace(file=parts[1], max_lines=max_lines))
            elif command == "hash":
                if len(parts) < 2:
                    print("Usage: hash <file> [algorithm]")
                    continue
                algorithm = parts[2] if len(parts) > 2 else "sha256"
                cmd_hash(argparse.Namespace(file=parts[1], algorithm=algorithm))
            elif command == "search":
                if len(parts) < 2:
                    print("Usage: search <regex> [path]")
                    continue
                target = parts[2] if len(parts) > 2 else "."
                cmd_search(
                    argparse.Namespace(
                        pattern=parts[1],
                        path=target,
                        ignore_case=True,
                        ext=[],
                        max_hits=50,
                    )
                )
            else:
                print(f"Unknown command: {command}")
        except ValueError as exc:
            print(f"Invalid value: {exc}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="brain_mix",
        description="Single-file offline Brain Mix utility.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    catalog = sub.add_parser("catalog", help="Show all subagents, modes, and skills")
    catalog.set_defaults(func=cmd_catalog)

    sysinfo = sub.add_parser("sysinfo", help="Show local system information")
    sysinfo.set_defaults(func=cmd_sysinfo)

    list_cmd = sub.add_parser("ls", help="List files/directories")
    list_cmd.add_argument("path", nargs="?", default=".", help="Path to list")
    list_cmd.set_defaults(func=cmd_ls)

    read_cmd = sub.add_parser("read", help="Read file preview")
    read_cmd.add_argument("file", help="File path")
    read_cmd.add_argument(
        "--max-lines",
        type=int,
        default=120,
        help="Maximum lines to print",
    )
    read_cmd.set_defaults(func=cmd_read)

    hash_cmd = sub.add_parser("hash", help="Hash a file")
    hash_cmd.add_argument("file", help="File path")
    hash_cmd.add_argument(
        "--algorithm",
        default="sha256",
        help="Hash algorithm: sha256 | sha1 | md5",
    )
    hash_cmd.set_defaults(func=cmd_hash)

    search_cmd = sub.add_parser("search", help="Regex search local files")
    search_cmd.add_argument("pattern", help="Regex pattern")
    search_cmd.add_argument("path", nargs="?", default=".", help="Root path")
    search_cmd.add_argument("--ignore-case", action="store_true", help="Case-insensitive")
    search_cmd.add_argument(
        "--ext",
        action="append",
        help="Limit to extension (repeatable), e.g. --ext py --ext md",
    )
    search_cmd.add_argument("--max-hits", type=int, default=100, help="Stop after N hits")
    search_cmd.set_defaults(func=cmd_search)

    repl_cmd = sub.add_parser("repl", help="Interactive offline shell")
    repl_cmd.set_defaults(func=cmd_repl)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
