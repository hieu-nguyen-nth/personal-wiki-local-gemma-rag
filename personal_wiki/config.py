from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class Config:
    project_dir: Path
    vault: Path
    model: Path
    data_dir: Path
    top_k: int = 5
    max_context_chars: int = 12_000
    max_tokens: int = 320
    chat_max_tokens: int = 520

    @property
    def database(self) -> Path:
        return self.data_dir / "index.sqlite3"

    @property
    def runs_dir(self) -> Path:
        return self.data_dir / "runs"

    @property
    def assistant_prompt(self) -> Path:
        return self.project_dir / "prompts" / "assistant.md"

    @property
    def research_prompt(self) -> Path:
        return self.project_dir / "prompts" / "research.md"


def load_config(path: Path | None = None) -> Config:
    project_dir = Path(__file__).resolve().parent.parent
    config_path = path or project_dir / "wiki_config.toml"
    with config_path.open("rb") as handle:
        raw = tomllib.load(handle)

    data_dir = Path(raw.get("data_dir", ".wiki-data")).expanduser()
    if not data_dir.is_absolute():
        data_dir = project_dir / data_dir
    vault = Path(raw["vault"]).expanduser()
    if not vault.is_absolute():
        vault = project_dir / vault
    model = Path(raw["model"]).expanduser()
    if not model.is_absolute():
        model = project_dir / model
    return Config(
        project_dir=project_dir,
        vault=vault,
        model=model,
        data_dir=data_dir,
        top_k=int(raw.get("top_k", 5)),
        max_context_chars=int(raw.get("max_context_chars", 12_000)),
        max_tokens=int(raw.get("max_tokens", 320)),
        chat_max_tokens=int(raw.get("chat_max_tokens", 520)),
    )
