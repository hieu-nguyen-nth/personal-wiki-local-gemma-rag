# Ingestion and Wiki Generation Evidence

## First local generation

Command:

```sh
./launch.command ingest --generate-wiki
```

Actual Terminal result:

```text
Scanned 14 files: 0 updated, 14 unchanged, 0 removed; wrote 0 new chunks.
Wiki page: wiki/AI and Product/AI-Powered Product Teams.md — generated; review required
Refreshed index: 2 updated, 13 unchanged.
```

Local Gemma read `raw/Product Management Is Dead, So What Are We Doing Instead?.md` and generated `wiki/AI and Product/AI-Powered Product Teams.md`. The harness added the descriptive filename, matching H1, source path/hash metadata, related-note links, original-source link, and index entry deterministically.

## Human review

The generated page was compared with the unchanged original source. Its claims about automating PM work, the anti-todo list, partial automation and refinement, time for users and creativity, skill development, generalist specialists, collapsing product/design/engineering boundaries, inbound/outbound PM work, and lean senior product groups were present in the source. All internal links resolved to exactly one file. The page was marked `review_status: "reviewed"`.

## Duplicate-safety rerun

The same generation command was run again. Actual result:

```text
Scanned 15 files: 1 updated, 14 unchanged, 0 removed; wrote 5 new chunks.
Wiki page: wiki/AI and Product/AI-Powered Product Teams.md — unchanged
Refreshed index: 0 updated, 15 unchanged.
Wiki files before: 9
Wiki files after: 9
Generated target copies: 1
review_status: "reviewed"
```

Assessment: pass. Re-ingestion recognized the unchanged source hash, preserved the reviewed page, kept the readable filename, and created no duplicate.
