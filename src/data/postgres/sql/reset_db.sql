DELETE FROM articles;
DELETE FROM found_videos;
DELETE FROM mentions;
DELETE FROM usable_videos;

CREATE TABLE IF NOT EXISTS articles (
  website_url TEXT NOT NULL,
  status      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS found_videos (
  website_url TEXT NOT NULL,
  platform    TEXT NOT NULL,
  video_url   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS mentions (
  event_id    INT  NOT NULL,
  website_url TEXT NOT NULL
);

/* After processing, this table holds all the videos that need to be downloaded. */
CREATE TABLE IF NOT EXISTS usable_videos (
  website_url TEXT NOT NULL,
  video_url   TEXT NOT NULL
);

CREATE INDEX articles_website_url ON articles (website_url);
CREATE INDEX found_videos_website_url ON found_videos (website_url);
