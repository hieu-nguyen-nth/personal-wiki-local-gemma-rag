# Assignment 4 — Personal Wiki with Local Gemma + RAG

This is an original Python CLI and harness, not a cloned sample app. It turns five public-safe source notes into a small Obsidian wiki and answers questions locally with a quantized Gemma model. Local mode is the default: retrieval, generation, citations, run logs, and the wiki all work without a cloud service.

## Device and model choice

Test device: macOS Tahoe 26.6.2, Apple M1 MacBook Air, 8 GB unified memory, and 23.85 GB free disk space when setup began. The selected model is [`mlx-community/Gemma4-E2B-IT-Text-int4`](https://huggingface.co/mlx-community/Gemma4-E2B-IT-Text-int4), about 2.5 GB on disk, run through MLX-VLM 0.7.2.

| Gemma option | Meaning | Decision for this Mac |
|---|---|---|
| E2B | About 2B effective parameters; quantized int4 | Selected. Leaves enough of 8 GB unified memory for macOS, inference, context, and retrieval. |
| E4B | About 4B effective parameters; larger weights and runtime buffers | Not selected. It is too close to this machine's practical memory limit. |
| 26B-A4B MoE | 26B total parameters, about 4B active per token | Not selected. Active parameters describe compute, not the full weight memory footprint; all expert weights still need storage/memory. |

The assignment does not require running all three models or buying hardware. Ollama, llama.cpp, and LM Studio are unnecessary here because MLX-VLM is the compatible local runtime.

## Setup and commands

Python 3.12 is required. The first setup needs internet only to install dependencies and download the model; normal use is local afterward.

```sh
chmod +x setup.sh launch.command run_final_offline_demo.command
./setup.sh
./launch.command ingest
./launch.command help
```

Core commands:

```sh
./launch.command chat
./launch.command ask "How does K-means update its centroids, and why should initialization be repeated?"
./launch.command search "retrieval ranking recommender systems"
./launch.command ingest --generate-wiki
./launch.command help
```

Inside chat, `/wiki <question>` explicitly retrieves notes, `/reset` clears the conversation, and `/exit` quits. `chat` keeps conversational context and normally does not search notes. `ask` is a fresh, neutral evidence-only request that never receives chat history. `search` prints original passages and paths without generation. `ingest` updates changed files, removes deleted files, and does not duplicate unchanged content.

## How the system is connected

| Layer | What it does |
|---|---|
| Retrieval tool | `personal_wiki/retrieval.py` chunks Markdown by headings, indexes it with local SQLite FTS5, and returns ranked passages. `search` restricts results to unchanged originals in `vault/raw/`. |
| RAG workflow | For `ask`: retrieve up to five passages → format numbered evidence → call local Gemma with research rules → validate citation numbers → answer or return `Insufficient evidence in the wiki.` |
| Harness | `personal_wiki/harness.py` manages modes, chat context, prompts, model calls, timing, citation validation, errors, and optional JSON outputs. |
| CLI | `personal_wiki/cli.py` exposes `chat`, `ask`, `search`, `ingest`, and `help`; `model.py` connects the harness to MLX-VLM. |

Assistant instructions and research rules are deliberately separate in `prompts/assistant.md` and `prompts/research.md`. Retrieved notes are treated as untrusted evidence, not instructions. Chunks, hashes, SQLite data, and saved outputs remain outside the Obsidian vault in `.wiki-data/`.

Retrieval uses Unicode tokenization, prefix matches, BM25 ranking, and a query-term overlap threshold. Markdown is split near 1,600 characters, `ask` retrieves five passages with a 12,000-character context ceiling, and generation is capped at 320 tokens. This simple local lexical design is transparent and fast, although semantic/hybrid retrieval would improve synonym handling.

## Wiki design and source traceability

`vault/raw/` contains unchanged copies of the five approved source notes. `vault/wiki/` contains nine reviewed topic pages in two folders, with short descriptive filenames, matching H1 headings, readable links, related-note links, and source links. `vault/index.md` groups the topics and catalogs every original. Machine IDs never appear in filenames or graph labels.

The manifest `vault/wiki_manifest.toml` gives Gemma a controlled source, title, target path, description, and related pages for generated wiki notes. Re-generation checks the source hash, updates the existing target instead of inventing a new filename, preserves a reviewed page unless `--force` is used, refreshes the index, and is tested for duplicate safety.

Obsidian verification:

- [Open note with matching filename, H1, links, and sources](evidence/screenshots/final/obsidian-open-note.png)
- [Grouped index and actual filenames](evidence/screenshots/final/obsidian-index.png)
- [Wiki-only graph with meaningful connected labels](evidence/screenshots/final/obsidian-graph-path-wiki.png)

## Acceptance tests and real results

Answerable `ask` questions:

1. How does K-means update its centroids, and why should initialization be repeated?
2. What roles do retrieval and ranking play in a recommender system?
3. What distinguishes an Operator from a Craftsperson in product leadership?

Unsupported question: **When was the Eiffel Tower completed?** It returned exactly `Insufficient evidence in the wiki.`

On 2026-09-27, Wi-Fi was turned off, the CLI was restarted, the index was rebuilt, all four questions ran, raw search ran, and chat plus a follow-up ran without cloud services or fallback. The complete unedited transcript is [evidence/final-offline-terminal.txt](evidence/final-offline-terminal.txt); the terminal completion screenshot is [here](evidence/screenshots/final/offline-terminal-completed.png).

| Offline check | Response time | Maximum resident set size | Peak memory footprint |
|---|---:|---:|---:|
| Fresh ingestion, 15 files / 88 chunks | 0.06 s wall time | 23.25 MiB | 13.09 MiB |
| K-means `ask` | 9.32 s | 796.14 MiB | 3.56 GiB |
| Recommender `ask` | 10.31 s | 1.74 GiB | 3.57 GiB |
| Product archetypes `ask` | 9.70 s | 1.93 GiB | 3.67 GiB |
| Unsupported `ask` | 0.00 s | 22.45 MiB | 12.34 MiB |
| Three-turn chat, total | 12.72 s | 1.91 GiB | 3.33 GiB |

System-wide free memory was 64% before and 32% after the complete run. A second ingestion reported 15 unchanged files and zero new chunks. Six automated tests verify idempotent re-ingestion, stale-file removal, navigation exclusion, raw-only search, selective chat retrieval, separation of `ask` from chat history, and collision-free saved outputs.

```sh
./launch.command ingest
.venv/bin/python -m unittest discover -s tests -v
```

To reproduce the offline demonstration, turn Wi-Fi off first, then run:

```sh
./run_final_offline_demo.command
```

The script refuses to proceed if Wi-Fi is on, sets Hugging Face and Transformers offline flags, starts separate CLI processes, measures memory with `/usr/bin/time -l`, and writes `evidence/final-offline-terminal.txt`.

## Limitations and improvements

The E2B model is small enough for this Mac but occasionally offers multiple drafts despite a one-draft instruction, and its prose can be awkward. Lexical retrieval can return overlapping passages and less-relevant related sections. A future version would add local embeddings plus keyword search, merge adjacent duplicate chunks, rerank evidence, and evaluate a stronger writing prompt. During testing, second-resolution run filenames could collide; saved outputs now include microseconds and an automated regression test covers the fix.

Do not commit model weights, `.wiki-data/`, credentials, or transient Obsidian workspace state. Anyone cloning the repository should run `./setup.sh` to obtain the public model checkpoint from its official model page.
