from sqlalchemy import true
from youtube_transcript_api import YouTubeTranscriptApi

with open('urls_unique2.txt', 'r') as urls_file:
    urls = urls_file.readlines()

search = " days "
found = False

for url in urls:
    try:
        srt = YouTubeTranscriptApi.get_transcript(url)
        for item in srt:
            if search in item['text']:
                print(url)
                print(item)
                found = True
    except:
        pass

