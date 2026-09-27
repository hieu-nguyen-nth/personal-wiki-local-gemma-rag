from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
import tomllib

from .config import Config
from .model import LocalGemma


@dataclass(frozen=True)
class BuildResult:
    target: Path
    status: str


def _manifest(vault: Path) -> list[dict]:
    path = vault / "wiki_manifest.toml"
    if not path.is_file():
        raise FileNotFoundError(f"Wiki manifest not found: {path}")
    with path.open("rb") as handle:
        return list(tomllib.load(handle).get("pages", []))


def _strip_model_wrapping(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:markdown)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    text = re.sub(r"^#\s+.*?\n+", "", text, count=1)
    return text.strip()


def _frontmatter_value(text: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*[\"']?([^\n\"']+)", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else None


def _update_index(vault: Path, title: str, description: str) -> None:
    index = vault / "index.md"
    text = index.read_text(encoding="utf-8")
    link = f"- [[{title}]] — {description}"
    if link in text:
        return
    marker = "\n## Source Catalog\n"
    if marker not in text:
        raise RuntimeError(f"Could not find Source Catalog section in {index}")
    text = text.replace(marker, f"\n{link}\n{marker}", 1)
    index.write_text(text, encoding="utf-8")


def build_wiki_pages(config: Config, *, force: bool = False) -> list[BuildResult]:
    model = LocalGemma(config.model)
    instructions = (config.project_dir / "prompts" / "wiki_builder.md").read_text(encoding="utf-8")
    results: list[BuildResult] = []

    for page in _manifest(config.vault):
        source_relative = Path(page["source"])
        target_relative = Path(page["target"])
        source = config.vault / source_relative
        target = config.vault / target_relative
        title = str(page["title"])
        description = str(page["description"])
        related = [str(item) for item in page.get("related", [])]

        if not source.is_file():
            raise FileNotFoundError(f"Manifest source not found: {source}")
        source_text = source.read_text(encoding="utf-8", errors="replace")
        source_hash = hashlib.sha256(source_text.encode("utf-8")).hexdigest()

        if target.exists() and not force:
            existing = target.read_text(encoding="utf-8", errors="replace")
            if _frontmatter_value(existing, "source_hash") == source_hash:
                _update_index(config.vault, title, description)
                results.append(BuildResult(target, "unchanged"))
                continue
            if _frontmatter_value(existing, "review_status") == "reviewed":
                results.append(BuildResult(target, "reviewed-source-changed; use --force to replace"))
                continue

        request = (
            f"TITLE: {title}\n"
            f"PURPOSE: {description}\n"
            f"SOURCE PATH: {source_relative.as_posix()}\n\n"
            f"SOURCE TEXT:\n{source_text[:14_000]}"
        )
        body = model.generate(
            [
                {"role": "system", "content": instructions},
                {"role": "user", "content": request},
            ],
            max_tokens=520,
            temperature=0.2,
            top_p=0.85,
        )
        body = _strip_model_wrapping(body)
        if not body:
            raise RuntimeError(f"Gemma returned an empty wiki page for {source_relative}")

        related_lines = "\n".join(f"- [[{item}]]" for item in related)
        source_stem = source.stem
        note = (
            "---\n"
            f'source_path: "{source_relative.as_posix()}"\n'
            f'source_hash: "{source_hash}"\n'
            'generated_by: "Gemma 4 E2B IT Text int4"\n'
            'review_status: "needs-review"\n'
            "---\n\n"
            f"# {title}\n\n"
            f"{body}\n\n"
            "## Related Notes\n\n"
            f"{related_lines}\n\n"
            "## Sources\n\n"
            f"- [[{source_stem}|Original source]]\n"
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(note, encoding="utf-8")
        _update_index(config.vault, title, description)
        results.append(BuildResult(target, "generated; review required"))
    return results

