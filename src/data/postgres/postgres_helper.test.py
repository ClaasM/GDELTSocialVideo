from src.data.postgres.postgres_helper import PostgresHelper

# TODO use a proper test suite, do this on a test db, etc.

sqlite_helper = PostgresHelper()

assert sqlite_helper.save_crawled("www.crawled.com") is None
assert sqlite_helper.is_crawled("www.crawled.com")
assert not sqlite_helper.is_crawled("www.not_crawled.com")

assert sqlite_helper.save_found_video_url("www.has_videos.com", "twitter", "www.video.com") is None
assert sqlite_helper.has_videos("www.has_videos.com")
assert not sqlite_helper.has_videos("www.doesnt_have_videos.com")

print(sqlite_helper.save_found_video_url("www.video.com", "facebook", "www.has_videos.com"))
