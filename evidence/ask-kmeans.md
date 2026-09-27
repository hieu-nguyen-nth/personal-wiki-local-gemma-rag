# Ask Evidence — K-means Centroids and Initialization

## Test definition

- Mode: `ask`
- Execution: local and offline
- Run date: 2026-09-27
- Model: Gemma 4 E2B IT Text int4 through MLX-VLM
- Question: How does K-means update its centroids, and why should initialization be repeated?
- Expected evidence: `raw/Unsupervised Learning.md`, Week 1; reviewed page `wiki/Machine Learning/Clustering and Anomaly Detection.md`

## Actual answer

K-means alternates between two operations: assigning each data point to its nearest centroid and moving each centroid to the mean of its assigned examples [1]. The process involves finding randomly selected points as the center of a cluster, assigning each point to its closest centroid, and then recomputing the centroid by taking the average of all points assigned to it, before moving the centroid again [2]. This two-step process is repeated until convergence is reached (no change in the centroid) [2].

Initialization of K-means is done by randomly picking $k$ training examples to set as the starting centroids [2]. Repeating the initialization with different starting points may lead to different local optima [1]. Therefore, repeated random initialization is recommended to give K-means multiple attempts at finding the best local optimum [1][2].

## Retrieved passages

[1] wiki/Machine Learning/Clustering and Anomaly Detection.md — Clustering and Anomaly Detection
K-means alternates two operations: assigning each example to its nearest centroid and moving each centroid to the mean of its assigned examples. Different initial centroids can produce different local optima, so the source recommends repeated random initialization and selecting the run with the lowest cost.

Choosing the number of clusters can use an elbow plot, but the best value may remain ambiguous. When clusters feed a later task, their usefulness for that downstream purpose can be a more practical selection criterion.

Anomaly detection estimates what normal examples look like and flags low-probability cases. Error analysis can reveal missing features when important anomalies are not detected.

[2] raw/Unsupervised Learning.md — Week 1 - Unsupervised Learning
- Clustering 	- What is clustering 		- clustering algorithm looks at a number of data points and automatically finds data points that are related or similar to each other. - applications of clustering 			- grouping similar news 			- market segmentation 			- analysis - dna, astronomical 	- k-means intuition & algorithm 		- most commonly used algorithm for clustering 		- step 1: find randomly x points as the center of a cluster, assign each point it its closet centroid 				-  K-means will repeatedly do two different things: assign points to cluster centroids and move cluster centroids 				- check each point about distant which center is the smallest 			- step 2: recompute the centroid: 				- look all the points, take average of them -> new centroid, then move the centroid 			- [attachment: Pasted image 20250423223103.png] 			- take it and repeat these 2 steps until converge result (no change in centroid) 	- Optimization objectives - cost function of total between cluster item and centroid 		- [attachment: Pasted image 20250423223643.png][attachment: Screenshot 2025-04-23 at 22.38.54.png] 		- initializing k-means 	- initializing k-means 		- steps 			- choose K < m (cluster < training example) 			- randomly pick k training example 			- Set u1. u2 equal to these K example as the starting point 		- with different initialization -> may end at local minimum 			-  if you want to give k means multiple shots at finding the best local optimum.

## Measurement and assessment

- Response time: **12.68 seconds**
- Assessment: **Pass.**
- Citation `[1]` supports the description of K-means alternating between point assignment and centroid updates, as well as repeated initialization because different starting centroids can produce different local optima.
- Citation `[2]` supports the detailed assignment, mean-update, convergence, and random-initialization steps.
- Any retrieved passages not cited in the answer were not used as factual support.
- The answer was generated during the final offline run after Wi-Fi was disabled and the CLI was restarted.

