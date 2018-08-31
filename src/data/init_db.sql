CREATE TABLE IF NOT EXISTS crawled_websites (website_url text);
CREATE TABLE IF NOT EXISTS found_videos (website_url text, video_id text); /*TODO video_id has fixed length*/
CREATE TABLE IF NOT EXISTS mentions (event_id int, website_url text);