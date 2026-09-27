from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .config import load_config
from .harness import RunResult, WikiHarness
from .retrieval import ingest
from .wiki_builder import build_wiki_pages


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wiki",
        description="Offline personal-wiki CLI powered by local Gemma and local retrieval.",
    )
    parser.add_argument("--config", type=Path, help="Path to wiki_config.toml")
    sub = parser.add_subparsers(dest="command", required=True)

    chat = sub.add_parser("chat", help="Conversational assistant; wiki lookup is opt-in")
    chat.add_argument("message", nargs="?", help="One message, or omit for an interactive session")
    chat.add_argument("--wiki", action="store_true", help="Retrieve optional wiki context")
    chat.add_argument("--save", action="store_true", help="Save the local result outside the vault")
    chat.add_argument(
        "--script",
        type=Path,
        help="Run non-empty lines from a local text file as one conversation",
    )

    ask = sub.add_parser("ask", help="Standalone evidence-only answer with citations")
    ask.add_argument("question")
    ask.add_argument("--save", action="store_true")

    search = sub.add_parser("search", help="Return original passages and paths; no generation")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=5)
    search.add_argument("--save", action="store_true")

    ingest_parser = sub.add_parser("ingest", help="Idempotently index Markdown/text sources")
    ingest_parser.add_argument("source", nargs="?", type=Path, help="Defaults to the configured vault")
    ingest_parser.add_argument(
        "--generate-wiki",
        action="store_true",
        help="Use local Gemma and the vault manifest to create/update readable wiki pages",
    )
    ingest_parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing generated wiki page when used with --generate-wiki",
    )
    sub.add_parser("help", help="Show command help")
    return parser


def _print_result(result: RunResult) -> None:
    print(result.answer)
    if result.mode == "ask" and result.passages and result.answer != "Insufficient evidence in the wiki.":
        print("\nEvidence paths:")
        for passage in result.passages:
            print(f"[{passage.rank}] {passage.path} — {passage.heading}")
    print(f"\n[{result.elapsed_seconds:.2f}s]")


def _search_result(query: str, passages: list, elapsed: float = 0.0) -> RunResult:
    if not passages:
        text = "No matching passages."
    else:
        blocks = []
        for passage in passages:
            blocks.append(
                f"[{passage.rank}] {passage.path} — {passage.heading}\n"
                f"score={passage.score:.6f}\n{passage.text}"
            )
        text = "\n\n".join(blocks)
    return RunResult("search", query, text, passages, elapsed)


def interactive_chat(harness: WikiHarness, use_wiki: bool, save: bool) -> int:
    print("Local chat ready. Commands: /wiki <question>, /reset, /exit")
    while True:
        try:
            message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            return 0
        if not message:
            continue
        if message == "/exit":
            print("Bye.")
            return 0
        if message == "/reset":
            harness.reset_chat()
            print("Conversation context cleared.")
            continue
        lookup = use_wiki
        if message.startswith("/wiki "):
            lookup = True
            message = message[6:].strip()
        result = harness.chat(message, use_wiki=lookup)
        print(f"Gemma: {result.answer}\n[{result.elapsed_seconds:.2f}s]\n")
        if save:
            print(f"Saved: {harness.save(result)}")


def scripted_chat(harness: WikiHarness, path: Path, use_wiki: bool, save: bool) -> int:
    if not path.is_file():
        raise FileNotFoundError(f"Chat script not found: {path}")
    messages = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not messages:
        raise RuntimeError(f"Chat script has no messages: {path}")
    print(f"Local scripted chat: {path}")
    for message in messages:
        print(f"You: {message}")
        result = harness.chat(message, use_wiki=use_wiki)
        print(f"Gemma: {result.answer}\n[{result.elapsed_seconds:.2f}s]\n")
        if save:
            print(f"Saved: {harness.save(result)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "help":
        parser.print_help()
        return 0
    config = load_config(args.config)

    if args.command == "ingest":
        source = args.source or config.vault
        stats = ingest(source, config.database)
        print(
            f"Scanned {stats.scanned} files: {stats.indexed} updated, "
            f"{stats.unchanged} unchanged, {stats.removed} removed; "
            f"wrote {stats.chunks} new chunks."
        )
        if args.generate_wiki:
            for built in build_wiki_pages(config, force=args.force):
                print(f"Wiki page: {built.target.relative_to(config.vault)} — {built.status}")
            refreshed = ingest(config.vault, config.database)
            print(
                f"Refreshed index: {refreshed.indexed} updated, "
                f"{refreshed.unchanged} unchanged."
            )
        return 0

    harness = WikiHarness(config)
    try:
        if args.command == "search":
            result = _search_result(
                args.query,
                harness.raw_search(args.query, args.limit, original_only=True),
            )
            _print_result(result)
        elif args.command == "ask":
            result = harness.ask(args.question)
            _print_result(result)
        elif args.command == "chat" and args.message:
            result = harness.chat(args.message, use_wiki=args.wiki)
            _print_result(result)
        elif args.command == "chat" and args.script:
            return scripted_chat(harness, args.script, args.wiki, args.save)
        else:
            return interactive_chat(harness, args.wiki, args.save)
        if getattr(args, "save", False):
            print(f"Saved: {harness.save(result)}")
        return 0
    except (FileNotFoundError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
