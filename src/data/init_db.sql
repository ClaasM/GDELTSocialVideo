CREATE TABLE IF NOT EXISTS crawled_websites (
  website_url TEXT NOT NULL,
  status      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS found_videos (
  website_url    NOT NULL REFERENCES crawled_websites (website_url),
  platform  TEXT NOT NULL,
  video_url TEXT NOT NULL
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

CREATE INDEX found_video_website_url_idx
  ON found_videos (website_url);
CREATE INDEX crawled_websites_website_url_idx
  ON crawled_websites (website_url);
