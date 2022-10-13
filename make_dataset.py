from youtube_transcript_api import YouTubeTranscriptApi

with open('titles_unique2.txt', 'r') as titles_file:
    titles = titles_file.readlines()

with open('urls_unique2.txt', 'r') as urls_file:
    urls = urls_file.readlines()


def get_video_transcript(video_id):
    # assigning srt variable with the list
    # of dictonaries obtained by the get_transcript() function
    srt = YouTubeTranscriptApi.get_transcript(video_id)
    results = ""    
    for item in srt:
        results += item['text'] + "\n"
    return results


with open('dataset2.txt', 'w', encoding='utf-8') as output_file:
    for url, title in zip(urls, titles):
        try:
            subtitles = get_video_transcript(url[:-1])
        except:
            continue
        output_file.write(title)
        output_file.write(subtitles)

