/*
Computes the features used to classify whether or not the videos on a hosts website are relevant.

Features per host and per platform (facebook, twitter, youtube):
- Mean: Mean number of videos per article, including articles without videos
- Standard Deviation: Deviation in the number of videos per article
- Sum: Sum of videos
- Number of Distinct videos
- Average distinct videos per article
- Distinct videos to total videos

Features per host:
- article_count: The number of articles from that host, including those that don't contain videos


*/


/* Start with a clean table */
DROP TABLE IF EXISTS hosts;
CREATE TABLE  hosts;

