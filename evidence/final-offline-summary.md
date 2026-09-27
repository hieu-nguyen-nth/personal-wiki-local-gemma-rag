# Final Offline Test Summary

Source of truth: [`final-offline-terminal.txt`](final-offline-terminal.txt), captured from the normal macOS Terminal on 2026-09-27. The script verified that Wi-Fi was off before continuing and enabled the Hugging Face and Transformers offline flags. No results below were invented or edited.

| Check | Observed result |
|---|---|
| Fresh restart and help | The CLI displayed `chat`, `ask`, `search`, `ingest`, and `help`. |
| Fresh ingestion | 15 files indexed into 88 chunks; approximately 0.06 seconds wall time. |
| Duplicate-safety re-ingestion | 15 unchanged files and zero new chunks. |
| Raw search | Returned original passages from `raw/Unsupervised Learning.md` without loading Gemma. |
| K-means ask | Grounded answer with citations; 12.68 seconds. |
| Recommender ask | Grounded answer with citations; 10.96 seconds. |
| Product-archetypes ask | Grounded answer with citations; 10.05 seconds. |
| Unsupported ask | Returned exactly `Insufficient evidence in the wiki.` in 0.00 seconds. |
| Three-turn chat | Capability explanation, mentor thank-you note, and a shorter follow-up using conversation context; 11.80 seconds total wall time. |
| Wiki-backed cited chat | Retrieved K-means passages and cited factual claims with `[1]` and `[2]`; 14.35 seconds. |

The highest peak memory footprint during the four final ask tests was 3,940,638,272 bytes, approximately 3.67 GiB, during the product-archetypes question. The highest maximum resident set size was 1,833,074,688 bytes, approximately 1.71 GiB. The three-turn chat peaked at approximately 3.34 GiB.

System-wide free memory changed from 41% before the final sequence to 31% afterward. All four ask commands created distinct microsecond-resolution saved-result filenames. Seven automated tests pass, including coverage for idempotent re-ingestion, stale-file removal, raw-only search, ask/chat separation, conversational retrieval-query cleanup, citation repair in wiki-backed chat, and collision-free saved outputs.

The individual evidence cards contain the exact retrieved passages, answers, citations, measurements, and human assessments:

- [K-means](ask-kmeans.md)
- [Recommender retrieval and ranking](ask-recommender-retrieval-ranking.md)
- [Product archetypes](ask-product-archetypes.md)
- [Unsupported Eiffel Tower question](ask-unsupported-eiffel-tower.md)
- [Chat and mode-boundary checks](chat-mode-check.md)