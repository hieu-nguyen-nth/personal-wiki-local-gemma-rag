# Clustering and Anomaly Detection

K-means alternates two operations: assigning each example to its nearest centroid and moving each centroid to the mean of its assigned examples. Different initial centroids can produce different local optima, so the source recommends repeated random initialization and selecting the run with the lowest cost.

Choosing the number of clusters can use an elbow plot, but the best value may remain ambiguous. When clusters feed a later task, their usefulness for that downstream purpose can be a more practical selection criterion.

Anomaly detection estimates what normal examples look like and flags low-probability cases. Error analysis can reveal missing features when important anomalies are not detected.

## Related Notes

- [[Machine Learning Evaluation]] — error analysis helps diagnose missed anomalies and identify useful features.

## Sources

- [[Unsupervised Learning#Week 1 - Unsupervised Learning|Original course note — Unsupervised Learning]]
