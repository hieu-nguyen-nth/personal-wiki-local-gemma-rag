# Ask Evidence — Recommender Retrieval and Ranking

## Test definition

- Mode: `ask`
- Execution: local and offline
- Run date: 2026-09-27
- Model: Gemma 4 E2B IT Text int4 through MLX-VLM
- Question: What roles do retrieval and ranking play in a recommender system?
- Expected evidence: `raw/Unsupervised Learning.md`, Week 2 — Recommender systems; reviewed page `wiki/Machine Learning/Recommender Systems.md`

## Actual answer

Retrieval and ranking are two steps in a production recommender system [1][3]. Retrieval is the step that gathers a large list of plausible item candidates [2]. The goal of retrieval is to focus on coverage, generating a large list of possible recommendations for the user [2].

Ranking follows the retrieval step, where the system fine-tunes and selects the best items from the retrieved candidates to recommend to the user [2]. The trade-off between retrieval and ranking is that retrieving more candidates can improve relevance, but it increases computation, so this tradeoff should be tested [1].

In the context of content-based filtering, which involves calculating vectors for users and items to find matches, the process is often described as two steps: retrieval and ranking, especially when recommending from a large catalog to scale the system [3]. Offline evaluation can also be used to test the relevance-versus-computation tradeoff in candidate retrieval [4].

## Retrieved passages

[1] wiki/Machine Learning/Recommender Systems.md — Recommender Systems
The source material contrasts collaborative and content-based recommendation. Collaborative filtering learns user and item representations from observed ratings. Mean normalization helps handle users or items with sparse ratings.

Content-based filtering uses user and item features, maps them to representation vectors, and scores a match using their similarity. A production recommender commonly separates retrieval from ranking: retrieval gathers plausible candidates, while ranking orders those candidates. Retrieving more candidates can improve relevance but increases computation, so the tradeoff should be tested.

[2] raw/Unsupervised Learning.md — Week 2 - Recommender systems
- the retrieval step (focus on coverage) will generate a large list of plausible item candidates. That tries to cover a lot of possible things you might recommend to the user and it's okay during the retrieval step. If you include a lot of items that the user is not likely to like, remember removing duplicates or no value items 			- during the ranking step will fine tune and pick the best items to recommend to the user,[attachment: Pasted image 20250504153007.png] 		- Special notes for retrieval: how many items to consider? - During the retrieval step, retrieving more items will tend to result in better performance. But the algorithm will end up being slower ->  recommend carrying out offline experiments to see how much retrieving additional items results in more relevant recommendations. [attachment: Pasted image 20250504153242.png] 	- ethical use of recommender systems 		- need to choose the goal of the rec system, some are helpful, some (eg last 3) are not[attachment: Pasted image 20250504153521.png] 	- TensorFlow implementation of content-based filtering[attachment: Pasted image 20250504154533.png] - Principal Component Analysis (optional, may not go) - **to check later** 	- Reducing the number of features to visualize it 		- to find one or more new axes, such as z so that when you measure your datas coordinates on the new axis, you end up still with very useful information

[3] raw/Unsupervised Learning.md — Week 2 - Recommender systems
- limitations of collaborative filtering 			- cold star problem, eg how to 				- rank new items that few users have rated 				- show something reasonable to new users who have rated few items 			- use side information about items or users 				- item: genre, movie stars, studio,.. - user: demographics (age, gender, location,..), expressed preferences - Content-based filtering 	- collaborative filtering vs content-based filtering 		- collaborative filtering, the general approach is that we would recommend items to you based on ratings of users who gave similar ratings as you. - content-based filtering: recommend items to you based on features of users and items to find a good match [attachment: Pasted image 20250504150946.png] 		- learning to match and calculate based on features -> compute these vectors, v_u for the users and v_m for the items over the movies, and then take dot products between them to try to find good matches. [attachment: Pasted image 20250504151359.png] 	- deep learning for content-based filtering 		- network architecture as follow with cost function and optimization to fine-tune th emodel [attachment: Pasted image 20250504151930.png] [attachment: Pasted image 20250504151739.png] 		- not only for joint prediction, movies and users can also be used independently to find similar thing, and performance can be optimized by pre-computed [attachment: Pasted image 20250504152227.png] 	- recommending from a large catalogue - to scale 		- two steps which are called the retrieval and ranking steps

[4] wiki/Machine Learning/Recommender Systems.md — Related Notes
- Machine Learning Evaluation — offline evaluation can test the relevance-versus-computation tradeoff in candidate retrieval.

## Measurement and assessment

- Response time: **10.96 seconds**
- Assessment: **Pass.**
- Citations `[1]`, `[2]`, and `[3]` support the explanation that retrieval gathers plausible candidates, ranking selects and orders the best candidates, and the two-stage design helps recommendation systems scale to large catalogs.
- Citation `[4]` supports using offline evaluation to examine the relevance-versus-computation tradeoff.
- Retrieved passages that were not cited were not used as factual support.
- The answer was generated during the final offline run after Wi-Fi was disabled and the CLI was restarted.

## Earlier failure and fix

An earlier run retrieved navigation-only content from `index.md`. Retrieval was changed so `index.md` is excluded from factual evidence and search mode is restricted to original files under `vault/raw/`. The final offline run shown above no longer includes `index.md`.