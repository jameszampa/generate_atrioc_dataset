import os
import cv2
import numpy as np
from youtube_transcript_api import YouTubeTranscriptApi
from moviepy.editor import *

with open('urls.txt', 'r') as urls_file:
    urls = urls_file.readlines()

i = 0
total_sec = 0
for j, url in enumerate(urls):
    print(url)
    starting = 0
    ending = 0
    id = url.split(",")[0]
    if len(url.split(",")) == 2:
        ending = int(url.split(",")[1][1:-1])
    else:
        starting = int(url.split(",")[1][1:])
        ending = int(url.split(",")[2][1:-1])

    path = os.path.join('raw_data', id + '.mp3')
    if not os.path.exists(path):
        print(path, " does not exisit")
        continue
    clip = AudioFileClip(path)
    try:
        srt = YouTubeTranscriptApi.get_transcript(url)
    except:
        print("cant get transcript")
        continue
    for k, item in enumerate(srt):
        try:
            if float(item['start']) > ending and ending != -1:
                print("after ending")
                continue
            if float(item['start']) < starting:
                print("before begining")
                continue
            if k + 1 > len(srt) - 1:
                sub_clip = clip.subclip(item['start'], item['start'] + item['duration'])
            else:
                og_cut_off = item['start'] + item['duration']
                next_start = srt[k + 1]['start']
                if next_start < og_cut_off:
                    sub_clip = clip.subclip(item['start'], next_start + 0.15)
                    total_sec += (next_start + 0.15) - item['start']
                else:
                    sub_clip = clip.subclip(item['start'], og_cut_off)
                    total_sec += (og_cut_off) - item['start']
                sub_clip.write_audiofile(os.path.join('data', str(i).zfill(6) + ".wav"), ffmpeg_params=["-ac", "1"])
                with open(os.path.join('data', str(i).zfill(6) + ".txt"), "w") as text_file:
                    text_file.write(item['text'])
        except:
            print("out of bounds error")
        i += 1
print("Total seconds saved: ", total_sec)
