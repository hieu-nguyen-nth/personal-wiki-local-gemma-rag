# Assignment 4 — Personal Wiki with Local Gemma + RAG

This is an original Python CLI and harness, not a cloned sample app. It turns five public-safe source notes into a small Obsidian wiki and answers questions locally with a quantized Gemma model. Local mode is the default: retrieval, generation, citations, run logs, and the wiki all work without a cloud service.

## Grading index

- **Implementation:** [CLI](personal_wiki/cli.py), [harness](personal_wiki/harness.py), [retrieval](personal_wiki/retrieval.py), [local Gemma adapter](personal_wiki/model.py), and [wiki builder](personal_wiki/wiki_builder.py)
- **Setup:** [setup script](setup.sh), [configuration](wiki_config.toml), and the commands below
- **Personal wiki:** [vault index](vault/index.md), [original sources](vault/raw/), [reviewed wiki pages](vault/wiki/), and [generation manifest](vault/wiki_manifest.toml)
- **Ask evaluations:** [K-means](evidence/ask-kmeans.md), [recommender retrieval and ranking](evidence/ask-recommender-retrieval-ranking.md), [product archetypes](evidence/ask-product-archetypes.md), and [unsupported Eiffel Tower question](evidence/ask-unsupported-eiffel-tower.md)
- **Mode checks:** [chat evaluation](evidence/chat-mode-check.md), [wiki-backed chat citations](evidence/chat-wiki-citation-terminal.txt), and [wiki-generation evidence](evidence/ingestion-wiki-generation.md)
- **Offline proof:** [final summary](evidence/final-offline-summary.md), [complete terminal transcript](evidence/final-offline-terminal.txt), [start screenshot showing Wi-Fi off](evidence/screenshots/final/offline-terminal-start.png), and [completion screenshot](evidence/screenshots/final/offline-terminal-completed.png)
- **Obsidian proof:** [open note](evidence/screenshots/final/obsidian-open-note.png), [topic-organized index](evidence/screenshots/final/obsidian-index.png), and [wiki-only graph](evidence/screenshots/final/obsidian-graph-path-wiki.png)

## Device and model choice

Test device: macOS Tahoe 26.6.2, Apple M1 MacBook Air, 8 GB unified memory, and 23.85 GB free disk space when setup began. System-wide memory was 41% free immediately before the final offline run and 31% free afterward. The selected checkpoint is [`mlx-community/Gemma4-E2B-IT-Text-int4`](https://huggingface.co/mlx-community/Gemma4-E2B-IT-Text-int4), a 2.67 GB int4 MLX conversion of Google's official [`google/gemma-4-E2B-it`](https://huggingface.co/google/gemma-4-E2B-it), run through MLX-VLM 0.7.2. The model family and available variants are documented in [Google's official Gemma documentation](https://ai.google.dev/gemma/docs/get_started).

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

### One command traced through the harness

For `./launch.command ask "How does K-means update its centroids?" --save`, `launch.command` selects the project virtual environment and invokes `wiki.py`. `personal_wiki/cli.py` parses `ask`, loads the configuration, and creates `WikiHarness`. `WikiHarness.ask` starts a fresh request without chat history, calls the local retrieval tool, formats the numbered evidence within the context limit, loads the research-only prompt, and calls local Gemma through `model.py`. The harness validates that the answer contains only valid passage citation numbers, the CLI displays the answer and evidence paths, and `--save` records the question, passages, answer, timing, and citations outside the vault.

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

Final offline `ask` evidence:

1. [K-means centroids and initialization](evidence/ask-kmeans.md)
2. [Recommender retrieval and ranking](evidence/ask-recommender-retrieval-ranking.md)
3. [Product leadership archetypes](evidence/ask-product-archetypes.md)
4. [Unsupported Eiffel Tower question](evidence/ask-unsupported-eiffel-tower.md), which returned exactly `Insufficient evidence in the wiki.`

Each card contains the expected sources, exact retrieved passages, actual Gemma answer, citations, response time, and a human assessment of whether the cited passages support the claims.

On 2026-09-27, Wi-Fi was turned off, the CLI was restarted, the index was rebuilt, all four questions ran, raw search ran, and chat plus a follow-up ran without cloud services or fallback. The complete unedited transcript is [evidence/final-offline-terminal.txt](evidence/final-offline-terminal.txt). The [start screenshot](evidence/screenshots/final/offline-terminal-start.png) shows the Wi-Fi-off check and fresh restart, while the [completion screenshot](evidence/screenshots/final/offline-terminal-completed.png) shows the completed run.

| Offline check | Response time | Maximum resident set size | Peak memory footprint |
|---|---:|---:|---:|
| Fresh ingestion, 15 files / 88 chunks | 0.06 s wall time | 23.38 MiB | 13.22 MiB |
| K-means `ask` | 12.68 s | 514.91 MiB | 3.42 GiB |
| Recommender `ask` | 10.96 s | 1.55 GiB | 3.57 GiB |
| Product archetypes `ask` | 10.05 s | 1.71 GiB | 3.67 GiB |
| Unsupported `ask` | 0.00 s | 22.42 MiB | 12.31 MiB |
| Three-turn chat, total | 11.80 s wall time | 1.61 GiB | 3.34 GiB |
| Wiki-backed cited chat | 14.35 s | Not separately measured | Not separately measured |

System-wide free memory was 41% before and 31% after the final offline sequence. A second ingestion reported 15 unchanged files and zero new chunks. Seven automated tests verify idempotent re-ingestion, stale-file removal, navigation exclusion, raw-only search, selective chat retrieval, conversational retrieval-query cleanup, citation repair in wiki-backed chat, separation of `ask` from chat history, and collision-free saved outputs.

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
