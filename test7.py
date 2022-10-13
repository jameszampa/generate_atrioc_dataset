import re
from youtube_transcript_api import YouTubeTranscriptApi


urls = 'urls4.txt'


def get_video_transcript(video_id):
    # assigning srt variable with the list
    # of dictonaries obtained by the get_transcript() function
    srt = YouTubeTranscriptApi.get_transcript(video_id)
    results = ""    
    for item in srt:
        results += item['text'] + "\n"
    return results


with open(urls, 'r') as urls_file:
    url_lines = urls_file.readlines()


yt_dict = {}
for url in url_lines[1:]:
    print(url)
    match = re.search(r"https://www.youtube.com/watch\?v=([a-zA-Z0-9_-]+)&list=UUgv4dPk_qZNAbUW9WkuLPSA&index=([0-9]+)", url)
    print(match[1])
    yt_dict[match[1]] = ""

with open("urls_unique3.txt", 'w') as urls_output_file:
    for key, value in yt_dict.items():
        urls_output_file.write(key)
        urls_output_file.write("\n")



