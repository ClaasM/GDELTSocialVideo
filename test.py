# populate article_videos and videos id's

import psycopg2

from src.data.videos import video as video_helper

conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
c = conn.cursor()
c.execute("SELECT url, platform from videos")

videos = c.fetchall()

print(len(videos))
counter = {"Success": 0, "Error": 0}
for index, (video_url, platform) in enumerate(videos):
    if index % 10000 == 0:
        print(index)
        print(counter)
    try:
        video_id = video_helper.get_id_from_url(video_url, platform)
        c.execute("UPDATE videos SET id=%s WHERE url=%s", [video_id, video_url])
        conn.commit()
        counter["Success"] += 1
    except Exception as e:
        print(e)
        print(video_url)
        counter["Error"] += 1

print(counter)
# videos = glob.glob(videos_path + "/*.mp4")
# print(len(videos))

# for video_path in videos:
#    video_id = video_path.split("/")[-1].split(".")[0]
#    c.execute("UPDATE videos SET crawling_status='Success' WHERE id=%s", [video_id])
#    conn.commit()
