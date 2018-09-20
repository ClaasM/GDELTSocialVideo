import psycopg2

conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
c = conn.cursor()
c.execute("SELECT DISTINCT video_url, platform FROM article_videos")
videos = c.fetchall()

for url, platform in videos:
    c.execute("INSERT INTO videos(url, platform) VALUES (%s,%s)", [url, platform])

conn.commit()