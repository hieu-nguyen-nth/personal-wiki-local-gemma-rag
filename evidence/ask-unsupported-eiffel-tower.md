# Ask Evidence — Unsupported Eiffel Tower Question

## Test definition

- Mode: `ask`
- Execution: local and offline
- Run date: 2026-09-27
- Model: `mlx-community/Gemma4-E2B-IT-Text-int4`
- Runtime: MLX-VLM 0.7.2
- Question: When was the Eiffel Tower completed?
- Expected behavior: no relevant retrieved evidence and an explicit insufficient-evidence response

## Retrieved passages

None. Retrieval found no passages meeting the relevance threshold.

## Actual response

> Insufficient evidence in the wiki.

## Measurement and assessment

- Response time: **0.00 seconds**
- Assessment: **Pass.**
- The harness stopped before loading Gemma because retrieval found no relevant evidence.
- It did not answer from model knowledge or use unrelated passages.
- This result was produced during the final offline run after Wi-Fi was disabled and the CLI was restarted.