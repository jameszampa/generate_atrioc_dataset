import urllib
import json
from youtube_transcript_api import YouTubeTranscriptApi


OUTPUT_FILE = "Ludwig.txt"


def get_video_transcript(video_id):
    # assigning srt variable with the list
    # of dictonaries obtained by the get_transcript() function
    srt = YouTubeTranscriptApi.get_transcript(video_id)
    
    with open(OUTPUT_FILE, "a") as output_txt_file:
        for item in srt:
            output_txt_file.write(item['text'] + "\n")


def get_all_video_in_channel(channel_id='UCrPseYLGpNygVi34QpGNqpA'):
    api_key = 'AIzaSyA_t5rGyYDinl_AHotxcoQ1JKwHxEN2VRI'
    base_video_url = 'https://www.youtube.com/watch?v='
    base_search_url = 'https://www.googleapis.com/youtube/v3/search?'

    first_url = base_search_url+'key={}&channelId={}&part=snippet,id&order=date&maxResults=25'.format(api_key, channel_id)

    video_links = []
    url = first_url
    while True:
        inp = urllib.request.urlopen(url)
        resp = json.load(inp)

        for i in resp['items']:
            if i['id']['kind'] == "youtube#video":
                video_links.append(base_video_url + i['id']['videoId'])

        try:
            next_page_token = resp['nextPageToken']
            url = first_url + '&pageToken={}'.format(next_page_token)
        except:
            break
    return video_links


prefix = 'https://www.youtube.com/watch?v='
links = get_all_video_in_channel()
with open(OUTPUT_FILE, "w") as output_file:
    for link in links:
        output_file.write(link + "\n")
