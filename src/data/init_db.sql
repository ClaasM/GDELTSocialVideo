/*
Create a database called "gdelt_social_video" first:
CREATE DATABASE gdelt_social_video;
Connect to it:
\c gdelt
Then run this script to initialize it.

This is not using any foreign keys on mentions and events because:
- Data might be incomplete (e.g. not every mention's event happened in the time frame that was downloaded)
- The data might only become available later and not for everything (i.e. not every mention_identifier is crawlable)
*/

-- TABLES

-- TODO this whole table might not be necessary
CREATE TABLE IF NOT EXISTS events (-- They are called "export" in the GDELT dataset, but events makes more sense
  -- Event ID and date attributes
  global_event_id          BIGINT PRIMARY KEY NOT NULL,
  sql_date                 INT    NOT NULL,
  month_year               INT    NOT NULL,
  year                     INT    NOT NULL,
  fraction_date            FLOAT  NOT NULL,
  -- Actor attributes
  actor1_code              TEXT,
  actor1_name              TEXT,
  actor1_country_code      TEXT,
  actor1_known_group_code  TEXT,
  actor1_ethnic_code       TEXT,
  actor1_religion1_code    TEXT,
  actor1_religion2_code    TEXT,
  actor1_type1_code        TEXT,
  actor1_type2_code        TEXT,
  actor1_type3_code        TEXT,
  actor2_code              TEXT,
  actor2_name              TEXT,
  actor2_country_code      TEXT,
  actor2_known_group_code  TEXT,
  actor2_ethnic_code       TEXT,
  actor2_religion1_code    TEXT,
  actor2_religion2_code    TEXT,
  actor2_type1_code        TEXT,
  actor2_type2_code        TEXT,
  actor2_type3_code        TEXT,
  -- Event action attributes
  is_root_event            BOOL   NOT NULL,
  event_code               TEXT   NOT NULL, -- These are "---" in very rare cases
  event_base_code          TEXT   NOT NULL,
  event_root_code          TEXT   NOT NULL,
  quad_class               INT    NOT NULL,
  goldstein_scale          FLOAT, -- This is null in very rare cases (TODO statistic)
  num_mentions             INT    NOT NULL,
  num_sources              INT    NOT NULL,
  num_articles             INT    NOT NULL,
  avg_tone                 FLOAT  NOT NULL,
  -- Event geography (actor 1)
  actor1_geo_type          INT    NOT NULL,
  actor1_geo_full_name     TEXT,
  actor1_geo_country_code  TEXT,
  actor1_geo_ADM1_code     TEXT,
  actor1_geo_ADM2_code     TEXT,
  actor1_geo_lat           FLOAT,
  actor1_geo_long          FLOAT,
  actor1_geo_feature_id    TEXT,
  -- Event geography (actor 2)
  actor2_geo_type          INT    NOT NULL,
  actor2_geo_fullName      TEXT,
  actor2_geo__country_code TEXT,
  actor2_geo_ADM1_code     TEXT,
  actor2_geo_ADM2_code     TEXT,
  actor2_geo_lat           TEXT,
  actor2_geo_long          TEXT,
  actor2_geo_feature_id    TEXT,
  -- Event geography (action)
  action_geo_type          INT    NOT NULL,
  action_geo_full_name     TEXT,
  action_geo_country_code  TEXT,
  action_geo_ADM1_code     TEXT,
  action_geo_ADM2_code     TEXT,
  action_geo_lat           TEXT,
  action_geo_long          TEXT,
  action_geo_feature_id    TEXT,
  -- Data management
  date_added               TEXT   NOT NULL,
  source_url               TEXT   NOT NULL -- Can't be a foreign key to Articles since it isn't actually always a url
);

CREATE TABLE IF NOT EXISTS mentions (
  -- Columns from the dataset
  global_event_id     BIGINT NOT NULL,
  event_time_date     BIGINT NOT NULL,
  mention_time_date   BIGINT NOT NULL,
  mention_type        INT    NOT NULL,
  mention_source_name TEXT, -- This is sometimes null (GDELT dataset impurities)
  mention_identifier  TEXT   NOT NULL,
  sentence_id         INT    NOT NULL,
  actor1_char_offset  INT    NOT NULL,
  actor2_char_offset  INT    NOT NULL,
  action_char_offset  INT    NOT NULL,
  in_raw_text         BOOL   NOT NULL,
  confidence          FLOAT  NOT NULL,
  mention_doc_len     INT    NOT NULL,
  mention_doc_tone    FLOAT  NOT NULL
);

CREATE TABLE IF NOT EXISTS articles (
  source_url      TEXT PRIMARY KEY NOT NULL, -- Those are the mention_identifiers that are url's (they not always are, see GDELT docs)
  source_name     TEXT NOT NULL,
  crawling_status TEXT DEFAULT 'Not Crawled'
);

-- Join table with some additional required information
CREATE TABLE IF NOT EXISTS article_videos (
  -- TODO delete unused columns
  source_url      TEXT NOT NULL,
  source_name     TEXT NOT NULL,
  platform        TEXT NOT NULL,
  video_id       TEXT NOT NULL,

  FOREIGN KEY (source_url) REFERENCES articles (source_url),
  FOREIGN KEY (video_id) REFERENCES videos (video_id)
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

-- INDICES
-- Indices are only created where they are really needed, because they take up space and slow down inserts/deletes
CREATE INDEX IF NOT EXISTS mentions_global_event_id_index
  ON public.mentions (global_event_id);
CREATE INDEX IF NOT EXISTS  mentions_mention_identifier_index
  ON public.mentions (mention_identifier);
CREATE INDEX IF NOT EXISTS  mentions_mention_source_name_index
  ON public.mentions (mention_source_name);
CREATE INDEX IF NOT EXISTS  events_source_url_index
  ON public.events (source_url);
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