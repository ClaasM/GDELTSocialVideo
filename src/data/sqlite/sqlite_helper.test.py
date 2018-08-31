from src.data.sqlite import sqlite_helper

# TODO use a proper test suite, do this on a test db, etc.

assert sqlite_helper.save_crawled("www.crawled.com") is None
assert sqlite_helper.is_crawled("www.crawled.com")
assert not sqlite_helper.is_crawled("www.not_crawled.com")

assert sqlite_helper.save_found_video("www.has_videos.com", "asdf") is None
assert sqlite_helper.has_videos("www.has_videos.com")
assert not sqlite_helper.has_videos("www.doesnt_have_videos.com")

print(sqlite_helper.save_mention(123, "www.has_videos.com"))
