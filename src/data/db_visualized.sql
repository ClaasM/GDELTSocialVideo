-- This is a copy of init_db used to create diagrams.
-- It has some slight differences to the actual data model, since the diagram software only supports mysql, and not postgres.
-- Also, some columns are omitted to increase readability
-- Cannot reference events since the event might've happened before the timeframe
-- TABLES

-- CREATE TYPE PLATFORM AS ENUM ('facebook', 'youtube', 'twitter'); (not supported by the database visualization)

CREATE TABLE IF NOT EXISTS events (
  global_event_id          BIGINT PRIMARY KEY NOT NULL,
  source_url               TEXT   NOT NULL
);

CREATE TABLE IF NOT EXISTS mentions (
  global_event_id     BIGINT NOT NULL,
  mention_source_name TEXT NOT NULL,
  mention_identifier  TEXT NOT NULL,

  FOREIGN KEY (global_event_id) REFERENCES events (global_event_id),
  FOREIGN KEY (mention_source_name) REFERENCES sources(source_name),
  FOREIGN KEY (mention_identifier) REFERENCES articles(source_url)
);

CREATE TABLE IF NOT EXISTS articles (
  source_url      TEXT PRIMARY KEY NOT NULL,
  crawling_status TEXT DEFAULT 'Not Crawled'
);

CREATE TABLE IF NOT EXISTS article_videos (
  platform        TEXT NOT NULL,
  video_id       TEXT NOT NULL,
  source_url       TEXT NOT NULL,

  FOREIGN KEY (source_url) REFERENCES articles (source_url),
  FOREIGN KEY (video_id, platform) REFERENCES videos (id, platform)
);

CREATE TABLE IF NOT EXISTS videos (
  id              TEXT NOT NULL,
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
  platform_relevant            BOOL
);

CREATE TABLE IF NOT EXISTS labeled_sources(
  source_name TEXT PRIMARY KEY,
  platform_relevant INTEGER,

  FOREIGN KEY (source_name) REFERENCES sources(source_name)

);
