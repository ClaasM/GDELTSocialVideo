import youtube_dl


video_id = "gKQ9EG7F7Xc"

ydl_opts = {
    # Download best format available but not better that 480p
    'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
    'outtmpl': video_id + '.%(ext)s',
}



    #size = info["filesize"]


    print(ret)
    # TODO this also has "dislike_count", "average_rating" etc.
