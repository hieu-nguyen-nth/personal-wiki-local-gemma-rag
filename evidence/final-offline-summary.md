# Final Offline Test Summary

Source of truth: `final-offline-terminal.txt`, captured from the normal macOS Terminal on 2026-09-27. Wi-Fi was reported off before the script continued. No outputs below were invented or edited.

| Check | Observed result |
|---|---|
| Fresh restart and help | CLI displayed all five modes. |
| Fresh ingestion | 15 updated files, 88 chunks; 0.06 s wall time. |
| Re-ingestion | 15 unchanged files, zero new chunks. |
| Raw search | Three original passages from `raw/Unsupervised Learning.md`; no Gemma call. |
| K-means ask | Evidence-supported response with `[1]` and `[2]`; 9.32 s. |
| Recommender ask | Evidence-supported response with `[1]`, `[2]`, and `[3]`; 10.31 s. |
| Product leadership ask | Evidence-supported response with citations; 9.70 s. |
| Unsupported ask | Exact response: `Insufficient evidence in the wiki.`; 0.00 s. |
| Chat | Casual capability answer, two-sentence mentor note, then a shorter revision using session context. |

The highest observed model-command peak memory footprint was 3,935,346,880 bytes (about 3.67 GiB), during the product-leadership question. The highest maximum resident set size was 2,068,054,016 bytes (about 1.93 GiB). The full chat process took 12.72 seconds. System-wide free memory changed from 64% before the sequence to 32% afterward.

One saved JSON filename collision was exposed because two commands completed within the same second. The terminal transcript retained both outputs. The code now uses microsecond timestamps, and `test_saved_runs_have_unique_names` prevents regression.
