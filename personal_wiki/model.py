from __future__ import annotations

from pathlib import Path
import re
from typing import Any


class LocalGemma:
    """Lazy MLX adapter; importing retrieval commands never loads the model."""

    def __init__(self, model_path: Path):
        self.model_path = model_path
        self._model: Any = None
        self._processor: Any = None

    def _load(self) -> None:
        if self._model is not None:
            return
        if not (self.model_path / "model.safetensors").is_file():
            raise RuntimeError(f"Local model is missing: {self.model_path}")
        try:
            from mlx_vlm import load
        except ImportError as error:
            if "No Metal device available" in str(error):
                raise RuntimeError(
                    "MLX cannot access Apple Metal in this headless shell. "
                    "Launch the command from the normal macOS Terminal app."
                ) from error
            raise RuntimeError(
                f"MLX-VLM could not be imported ({error}). Run ./setup.sh once while online."
            ) from error
        self._model, self._processor = load(str(self.model_path))

    def generate(
        self,
        messages: list[dict[str, str]],
        *,
        max_tokens: int,
        temperature: float,
        top_p: float = 0.9,
    ) -> str:
        self._load()
        from mlx_vlm import generate
        from mlx_vlm.prompt_utils import apply_chat_template

        prompt = apply_chat_template(
            self._processor,
            self._model.config,
            messages,
            num_images=0,
            num_audios=0,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        result = generate(
            model=self._model,
            processor=self._processor,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            verbose=False,
        )
        text = str(getattr(result, "text", result)).strip()
        # Some Gemma templates emit escaped Markdown markers as visible text.
        return re.sub(r"\\+([*_])", r"\1", text)
