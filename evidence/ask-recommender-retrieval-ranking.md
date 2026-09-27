# Ask Evidence — Recommender Retrieval and Ranking

## Test definition

- Mode: `ask`
- Execution: local
- Model: Gemma 4 E2B IT Text int4 through MLX-VLM
- Question: What roles do retrieval and ranking play in a recommender system?
- Expected evidence: `raw/Unsupervised Learning.md`, Week 2 — Recommender systems; reviewed page `wiki/Machine Learning/Recommender Systems.md`

## Actual answer

Retrieval and ranking are two steps in a production recommender system [1][4]. Retrieval is the initial step that gathers a large list of plausible item candidates [3]. The goal of retrieval is to cover a wide range of possible recommendations for the user [3].

Ranking follows the retrieval step, where the system fine-tunes and selects the best items from the retrieved list to recommend to the user [3]. The choice of how many items to retrieve can be tested through offline experiments to determine how additional retrieval results affect the relevance of the recommendations [3]. This two-step process is used when recommending from a large catalog to scale the system [4].

## Evidence paths reported by the CLI

1. `wiki/Machine Learning/Recommender Systems.md` — Recommender Systems
2. `index.md` — Machine Learning
3. `raw/Unsupervised Learning.md` — Week 2 - Recommender systems
4. `raw/Unsupervised Learning.md` — Week 2 - Recommender systems
5. `index.md` — Source Catalog

## Measurement

- Response time reported by the CLI: **18.99 seconds**
- Memory measurement: pending final offline run

## Assessment

Pass. The answer correctly describes retrieval as candidate generation and ranking as selection/ordering. Citations `[1]`, `[3]`, and `[4]` point to the reviewed recommender page and the original course-note section containing those claims. The result does not rely on chat history or uncited general knowledge for its material claims.

Observed retrieval limitation: `index.md` appeared as results `[2]` and `[5]` even though the underlying reviewed and raw notes were stronger evidence. A future improvement is to down-rank navigation-only pages or label them as non-evidence.

## Fix and rerun

The retrieval rules were changed so navigation-only `index.md` is never treated as factual evidence. Search mode was also restricted to unchanged originals under `raw/`; ask mode may use both `raw/` evidence and reviewed `wiki/` pages.

### Actual rerun answer

The Terminal emitted literal escaped Markdown markers (`\*` and `\*\*`) around the two bullets. They are normalized below for readability; the wording and citations are unchanged.

Retrieval and ranking are two steps in a production recommender system [1][3].

- **Retrieval:** This step focuses on coverage and generates a large list of plausible item candidates [2]. The goal is to cover many possible recommendations for the user, and including more items during retrieval tends to result in better performance [2]. However, retrieving more items increases computation, so this trade-off should be tested [1].
- **Ranking:** This step refines the list created by retrieval, ordering the candidates to select the best items to recommend to the user [1][2].

In summary, retrieval gathers plausible candidates, and ranking orders those candidates [1]. This two-step process is used when recommending from a large catalog to scale the system [3].

### Rerun evidence paths

1. `wiki/Machine Learning/Recommender Systems.md` — Recommender Systems
2. `raw/Unsupervised Learning.md` — Week 2 - Recommender systems
3. `raw/Unsupervised Learning.md` — Week 2 - Recommender systems
4. `wiki/Machine Learning/Recommender Systems.md` — Sources
5. `raw/Unsupervised Learning.md` — Week 2 - Recommender systems

### Rerun assessment

Pass. No navigation page appears in the evidence. The claims about candidate coverage, ranking, computation trade-offs, and large-catalog scaling are supported by citations `[1]`, `[2]`, and `[3]`. Response time was **11.71 seconds**. This is recorded as an observed warm rerun, not proof that the code change alone caused the speed difference.
