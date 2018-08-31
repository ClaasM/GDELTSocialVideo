CREATE TABLE IF NOT EXISTS crawled_websites (website_url text, status text);
CREATE TABLE IF NOT EXISTS found_videos (website_url text, video_url text);
CREATE TABLE IF NOT EXISTS mentions (event_id int, website_url text);
/* After processing, this table holds all the videos that need to be downloaded. */
CREATE TABLE IF NOT EXISTS usable_videos(website_url text, video_url text)