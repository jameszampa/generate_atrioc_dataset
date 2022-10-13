from pytube import YouTube
import os
from youtube_transcript_api import YouTubeTranscriptApi


with open('urls.txt', 'r') as urls_file:
    urls = urls_file.readlines()

for i, url in enumerate(urls):
    print(i, len(urls))
    try:
        id = url.split(",")[0] # url[:-1]
        print(id)
        yt = YouTube('https://www.youtube.com/watch?v=' + id)
        video = yt.streams.filter(only_audio=True).first()
        out_file = video.download(filename=id + '.mp4')
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        print(out_file, new_file)
        os.rename(out_file, new_file)
        print(yt.title + " has been successfully downloaded.")
    except:
        continue

