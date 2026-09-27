# Recommender Systems

The source material contrasts collaborative and content-based recommendation. Collaborative filtering learns user and item representations from observed ratings. Mean normalization helps handle users or items with sparse ratings.

Content-based filtering uses user and item features, maps them to representation vectors, and scores a match using their similarity. A production recommender commonly separates retrieval from ranking: retrieval gathers plausible candidates, while ranking orders those candidates. Retrieving more candidates can improve relevance but increases computation, so the tradeoff should be tested.

## Related Notes

- [[Machine Learning Evaluation]] — offline evaluation can test the relevance-versus-computation tradeoff in candidate retrieval.

## Sources

- [[Unsupervised Learning#Week 2 - Recommender systems|Original course note — Recommender systems]]
