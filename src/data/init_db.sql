CREATE TABLE IF NOT EXISTS crawled_websites (
  website_url TEXT PRIMARY KEY NOT NULL,
  status TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS found_videos (
  website_url NOT NULL REFERENCES crawled_websites(website_url),
  video_url TEXT PRIMARY KEY NOT NULL,
  );

CREATE TABLE IF NOT EXISTS mentions (event_id int, website_url text);
/* After processing, this table holds all the videos that need to be downloaded. */
CREATE TABLE IF NOT EXISTS usable_videos(website_url text, video_url text)


  CREATE TABLE Price (
  PriceId INTEGER       PRIMARY KEY AUTOINCREMENT NOT NULL,
  Name    VARCHAR(100)  NOT NULL,
  Type    CHAR(1)       NOT NULL DEFAULT ('M') REFERENCES PriceType(Type)
);

CREATE TABLE PriceType (
  Type    CHAR(1)       PRIMARY KEY NOT NULL,
  Seq     INTEGER
);
INSERT INTO PriceType(Type, Seq) VALUES ('M',1);
INSERT INTO PriceType(Type, Seq) VALUES ('R',2);
INSERT INTO PriceType(Type, Seq) VALUES ('H',3);