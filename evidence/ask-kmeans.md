# Ask Evidence — K-means Centroids and Initialization

## Test definition

- Mode: `ask`
- Execution: local
- Model: Gemma 4 E2B IT Text int4 through MLX-VLM
- Question: How does K-means update its centroids, and why should initialization be repeated?
- Expected evidence: `raw/Unsupervised Learning.md`, Week 1; reviewed page `wiki/Machine Learning/Clustering and Anomaly Detection.md`

## Actual answer

K-means alternates between two operations: assigning each data point to its nearest centroid and updating each centroid to the mean of its assigned points [2]. Specifically, the steps involve:

1. Assigning points to cluster centroids [2].
2. Recomputing the centroid by taking the average of all points assigned to it, and then moving the centroid [2].

This process of assigning points and recomputing centroids is repeated until the result converges, meaning there is no change in the centroid [2].

Initialization of K-means involves randomly picking $k$ training examples to set as the starting centroids [2]. Repeating this initialization with different random choices can lead to different local optima [2]. Therefore, repeated random initialization is recommended to give K-means multiple opportunities to find the best local optimum [2].

## Evidence paths reported by the CLI

1. `wiki/Machine Learning/Clustering and Anomaly Detection.md` — Clustering and Anomaly Detection
2. `raw/Unsupervised Learning.md` — Week 1 - Unsupervised Learning
3. `wiki/AI and Product/AI-First Product Management.md` — AI-First Product Management
4. `raw/Unsupervised Learning.md` — Week 1 - Unsupervised Learning
5. `raw/Product Management Is Dead, So What Are We Doing Instead?.md` — Some takeaway / Notes

## Measurement and assessment

- Response time: **11.67 seconds**
- Assessment: pass. Citation `[2]` supports centroid assignment, mean updates, convergence, random initialization, and local-optimum reasoning.
- Retrieval limitation: results `[3]` and `[5]` were irrelevant but were not cited. The lexical-overlap threshold was strengthened before the offline rerun.

