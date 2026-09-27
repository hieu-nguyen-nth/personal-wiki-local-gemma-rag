# Ask Evidence — Unsupported Eiffel Tower Question

## Test definition

- Mode: `ask`
- Execution: local
- Question: When was the Eiffel Tower completed?
- Expected behavior: no relevant retrieved evidence and an explicit insufficient-evidence response

## Actual response

> Insufficient evidence in the wiki.

## Measurement and assessment

- Response time: **0.00 seconds**
- Retrieved passages: none
- Assessment: pass. The harness stopped before loading Gemma because retrieval found no relevant evidence. It did not answer from the model's general knowledge.
