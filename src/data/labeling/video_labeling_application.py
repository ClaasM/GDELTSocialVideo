"""
A small command line tool to make the labeling videos easier.
Possible labels are: amateur (1), edited (2), professional (3)
Whereas edit videos might include snippets of amateur footage with voice overlay, e.g. news reports,
and professional does not include any amateur footage (e.g. music videos, movie trailers)

TODO What percentage is already covered by amateur, news, trailer, music,


TODO print introduction or something
TODO also print total number of videos already labeled

TODO maybe use moviepy: my_clip.preview(fps=15, audio=False) # don't generate/play the audio.
"""

import psycopg2
from random import shuffle
import cv2

from src.visualization import console
from src.data.videos import video as video_helper

if __name__ == "__main__":
    conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
    c = conn.cursor()

    # Create a cursor for every video that hasn't been labeled yet.
    c.execute("""SELECT videos.id, videos.platform FROM videos
                  LEFT JOIN labeled_videos  ON (labeled_videos.id, labeled_videos.platform) = (videos.id, videos.platform)
                  WHERE labeled_videos.relevant IS NULL AND videos.crawling_status='Success'""")
    videos = c.fetchall()
    shuffle(videos)

    for (video_id, platform) in videos:
        video_path = video_helper.get_path(platform) + "/" + video_id + ".mp4"

        # Play the video video
        print(video_path)

        stream = cv2.VideoCapture(video_path)

        cv2.namedWindow("frame")
        cv2.moveWindow('frame', 200, 200)

        fps = stream.get(cv2.CAP_PROP_FPS)
        waitPerFrameInMillisec = int(1 / fps * 1000 / 1)

        print('Frame Rate = ', fps, ' frames per sec')

        while stream.isOpened():
            ret, frame = stream.read()
            cv2.imshow('frame', frame)

            if cv2.waitKey(waitPerFrameInMillisec) & 0xFF == ord('q'):
                break

        stream.release()
        cv2.destroyAllWindows()

        relevance = input("""
        Is this video amateur footage?
        1: Yes
        2: No (edited, e.g. news coverage with voice over and snippets of amateur footage)
        3: No (professional, containing no significant amateur footage at all, e.g. a music video)
        """)

        # c.execute("INSERT INTO labeled_videos (platform, id, relevant) VALUES (%s, %s, %s)",
        #          [platform, video_id, relevance])
        conn.commit()
        print()
