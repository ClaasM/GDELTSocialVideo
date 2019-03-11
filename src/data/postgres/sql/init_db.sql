--

-- TABLES

CREATE TABLE IF NOT EXISTS articles (
  source_url      TEXT PRIMARY KEY NOT NULL, -- Those are the mention_identifiers that are url's (they not always are, see GDELT docs)
  source_name     TEXT NOT NULL,
  crawling_status TEXT DEFAULT 'Not Crawled'
);

-- Join table with some additional required information
CREATE TABLE IF NOT EXISTS article_videos (
  source_url      TEXT NOT NULL,
  source_name     TEXT NOT NULL,
  platform        TEXT NOT NULL,
  video_id       TEXT NOT NULL,

  FOREIGN KEY (source_url) REFERENCES articles (source_url),
  FOREIGN KEY (video_id) REFERENCES videos (id)
);

CREATE TABLE IF NOT EXISTS videos (
  id        TEXT NOT NULL, --the video_id is extracted from the url when crawling it (to make querying for it faster).
  platform        TEXT NOT NULL,
  crawling_status TEXT DEFAULT 'Not Crawled',
  comments        INT,
  shares          INT,
  likes           INT,
  views           INT,
  duration        INT,

  PRIMARY KEY (platform, id)
);

CREATE TABLE  IF NOT EXISTS sources (
  source_name           TEXT PRIMARY KEY NOT NULL,
  article_count         INT DEFAULT 1,
  -- Features are computed later
  twitter_std_dev       FLOAT,
  twitter_sum           INT,
  twitter_count         INT,
  twitter_sum_distinct  INT,
  youtube_std_dev       FLOAT,
  youtube_sum           INT,
  youtube_count         INT,
  youtube_sum_distinct  INT,
  facebook_std_dev      FLOAT,
  facebook_sum          INT,
  facebook_count        INT,
  facebook_sum_distinct INT,
  -- <platform>_std_dev       FLOAT,
  -- <platform>_sum           INT,
  -- <platform>_count         INT,
  -- <platform>_sum_distinct  INT,
  -- Relevancy is determined by the classifier
  -- Relevancy is determined by the classifier
  twitter_relevant            BOOL,
  youtube_relevant            BOOL,
  facebook_relevant           BOOL
);

CREATE TABLE IF NOT EXISTS labeled_sources(
  source_name TEXT PRIMARY KEY,
  youtube_relevant INTEGER,
  twitter_relevant INTEGER,
  facebook_relevant INTEGER
);

CREATE TABLE IF NOT EXISTS labeled_videos (
  id TEXT,
  platform TEXT,
  relevant INTEGER,

  PRIMARY KEY (platform, id)
);

CREATE INDEX IF NOT EXISTS  articles_crawling_status_index
  ON public.articles (crawling_status);
CREATE INDEX IF NOT EXISTS  article_videos_platform_index
  ON public.article_videos (platform);
CREATE INDEX IF NOT EXISTS  article_videos_source_name_index
  ON public.article_videos (source_name);
CREATE INDEX IF NOT EXISTS  article_videos_video_id_index
  ON public.article_videos USING HASH (video_id);
CREATE INDEX IF NOT EXISTS  article_videos_source_name_index
  ON public.article_videos (source_name);
CREATE INDEX IF NOT EXISTS  source_twitter_relevant_index
  ON sources (twitter_relevant);
CREATE INDEX IF NOT EXISTS  source_youtube_relevant_index
  ON sources (youtube_relevant);
CREATE INDEX IF NOT EXISTS  source_facebook_relevant_index
  ON sources (facebook_relevant);