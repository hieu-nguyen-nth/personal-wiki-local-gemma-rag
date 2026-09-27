from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import time

from .config import Config
from .model import LocalGemma
from .retrieval import Passage, format_evidence, search


INSUFFICIENT = "Insufficient evidence in the wiki."
CITATION_RE = re.compile(r"\[(\d+)\]")


@dataclass(frozen=True)
class RunResult:
    mode: str
    query: str
    answer: str
    passages: list[Passage]
    elapsed_seconds: float


class WikiHarness:
    def __init__(self, config: Config):
        self.config = config
        self.model = LocalGemma(config.model)
        self.chat_history: list[dict[str, str]] = []

    @staticmethod
    def _read_prompt(path: Path) -> str:
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            raise RuntimeError(f"Prompt file is empty: {path}")
        return text

    def raw_search(
        self,
        query: str,
        limit: int | None = None,
        *,
        original_only: bool = False,
    ) -> list[Passage]:
        return search(
            self.config.database,
            query,
            limit or self.config.top_k,
            original_only=original_only,
        )

    @staticmethod
    def _chat_needs_wiki(message: str) -> bool:
        lowered = message.lower()
        cues = (
            "my notes",
            "my wiki",
            "personal wiki",
            "according to my notes",
            "based on my notes",
            "from my notes",
            "what did i write",
        )
        return any(cue in lowered for cue in cues)

    @staticmethod
    def _chat_retrieval_query(message: str) -> str:
        query = message
        wrappers = (
            "what do my notes say about",
            "what does my wiki say about",
            "what did i write about",
            "according to my notes",
            "based on my notes",
            "from my notes",
            "in my notes",
            "my notes",
            "my wiki",
            "personal wiki",
            "what did i write",
        )
        for wrapper in wrappers:
            query = re.sub(re.escape(wrapper), " ", query, flags=re.IGNORECASE)
        query = re.sub(r"\s+", " ", query).strip(" ?.,")
        return query or message

    @staticmethod
    def _citations_are_valid(answer: str, passage_count: int) -> bool:
        cited = {int(value) for value in CITATION_RE.findall(answer)}
        valid = set(range(1, passage_count + 1))
        return bool(cited) and cited.issubset(valid)

    def ask(self, question: str) -> RunResult:
        started = time.perf_counter()
        passages = self.raw_search(question)
        if not passages:
            return RunResult("ask", question, INSUFFICIENT, [], time.perf_counter() - started)
        evidence = format_evidence(passages, self.config.max_context_chars)
        messages = [
            {"role": "system", "content": self._read_prompt(self.config.research_prompt)},
            {"role": "user", "content": f"QUESTION:\n{question}\n\nEVIDENCE:\n{evidence}"},
        ]
        answer = self.model.generate(
            messages,
            max_tokens=self.config.max_tokens,
            temperature=0.1,
            top_p=0.8,
        )
        cited = {int(value) for value in CITATION_RE.findall(answer)}
        valid = set(range(1, len(passages) + 1))
        if answer != INSUFFICIENT and (not cited or not cited.issubset(valid)):
            answer = INSUFFICIENT
        return RunResult("ask", question, answer, passages, time.perf_counter() - started)

    def chat(self, message: str, *, use_wiki: bool = False) -> RunResult:
        started = time.perf_counter()
        lookup = use_wiki or self._chat_needs_wiki(message)
        retrieval_query = self._chat_retrieval_query(message)
        passages = self.raw_search(retrieval_query, 3) if lookup else []
        user_content = message
        if passages:
            evidence = format_evidence(passages, self.config.max_context_chars // 2)
            user_content += f"\n\nOPTIONAL PERSONAL-WIKI CONTEXT:\n{evidence}"
        messages = [
            {"role": "system", "content": self._read_prompt(self.config.assistant_prompt)},
            *self.chat_history,
            {"role": "user", "content": user_content},
        ]
        answer = self.model.generate(
            messages,
            max_tokens=self.config.chat_max_tokens,
            temperature=0.75,
        )
        if passages and not self._citations_are_valid(answer, len(passages)):
            correction = (
                "Revise your previous answer. Cite every factual claim drawn from "
                "the personal-wiki evidence using valid passage numbers such as [1]. "
                "Keep suggestions clearly labeled and do not invent personal facts."
            )
            answer = self.model.generate(
                [
                    *messages,
                    {"role": "assistant", "content": answer},
                    {"role": "user", "content": correction},
                ],
                max_tokens=self.config.chat_max_tokens,
                temperature=0.2,
            )
            if not self._citations_are_valid(answer, len(passages)):
                answer = (
                    "I could not produce a reliably cited answer from the retrieved "
                    "personal-wiki passages. Please use ask mode for an evidence-only answer."
                )

        self.chat_history.extend([
            {"role": "user", "content": message},
            {"role": "assistant", "content": answer},
        ])
        self.chat_history = self.chat_history[-12:]
        return RunResult("chat", message, answer, passages, time.perf_counter() - started)

    def reset_chat(self) -> None:
        self.chat_history.clear()

    def save(self, result: RunResult) -> Path:
        self.config.runs_dir.mkdir(parents=True, exist_ok=True)
        # Microseconds keep back-to-back commands from overwriting one another.
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        path = self.config.runs_dir / f"{stamp}-{result.mode}.json"
        payload = asdict(result)
        payload["saved_at"] = datetime.now(timezone.utc).isoformat()
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path
