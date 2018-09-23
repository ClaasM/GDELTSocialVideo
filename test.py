import ffprobe

metadata=ffprobe.FFProbe("data/raw/videos/facebook/993318958828.mp4")

for stream in metadata.streams:
    if stream.isVideo():
            print("Stream contains "+stream.frames()+" frames.")