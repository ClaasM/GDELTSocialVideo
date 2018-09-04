DELETE FROM crawled_websites;
DELETE FROM found_videos;
DELETE FROM mentions;
DELETE FROM usable_videos;

CREATE TABLE IF NOT EXISTS crawled_websites (
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