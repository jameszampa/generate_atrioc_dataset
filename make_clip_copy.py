import time
import os
import websockets
from youtube_transcript_api import YouTubeTranscriptApi
from moviepy.editor import *
import json
import wave
import asyncio
import sys
import docker


async def get_vosk_prediction(wf):
    output_results = {'result': [],
                      'text': None}
    async with websockets.connect('ws://localhost:2700') as websocket: 
        await websocket.send('{ "config" : { "sample_rate" : %d } }' % (wf.getframerate()))
        buffer_size = int(wf.getframerate() * 0.2) # 0.2 seconds of audio
        while True:
            data = wf.readframes(buffer_size)

            if len(data) == 0:
                break

            await websocket.send(data)
            result = json.loads(await websocket.recv())
            if 'partial' in result.keys():
                continue
            elif 'result' in result.keys() and 'text' in result.keys():
                output_results['result'] += result['result']
                if output_results['text'] is None:
                    output_results['text'] = result['text']
                else:
                    output_results['text'] = " ".join(output_results['text'].split(' ') + result['text'].split(' '))

        await websocket.send('{"eof" : 1}')
        try:
            result = json.loads(await websocket.recv())
            if 'partial' in result.keys():
                pass
            elif 'result' in result.keys() and 'text' in result.keys():
                output_results['result'] += result['result']
                if output_results['text'] is None:
                    output_results['text'] = result['text']
                else:
                    output_results['text'] = " ".join(output_results['text'].split(' ') + result['text'].split(' '))
        except Exception as e:
            print("Vosk error:", e)
            
        return output_results


def contains_garabge(text):
    if "[ __ ]" in text:
        print(text)
        return True
    if "[Music]" in text:
        print(text)
        return True
    if "[Laughter]" in text:
        print(text)
        return True
    if "[Applause]" in text:
        print(text)
        return True
    return False


def read_urls_files():
    with open('urls.txt', 'r') as urls_file:
        urls = urls_file.readlines()

    with open('urls_unique2.txt') as urls_file:
        urls += urls_file.readlines()

    with open('urls_unique4.txt') as urls_file:
        urls += urls_file.readlines()
    
    return urls


def start_vosk():
    try:
        container = docker_client.containers.get("vosk")
    except:
        docker_client.containers.run(image='alphacep/kaldi-en-gpu:latest',
                                    device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])],
                                    detach=True,
                                    stdin_open=True,
                                    name='vosk',
                                    tty=True,
                                    ports={"2700/tcp": 2700},
                                    remove=True,
                                    auto_remove=True)
        time.sleep(5)
        container = docker_client.containers.get("vosk")
        return container

docker_client = docker.from_env()
start_vosk()

urls = read_urls_files()
i = 0
total_sec = 0
for j, url in enumerate(urls):
    print(j, len(urls))
    starting = 0
    ending = 0
    if "," in url:
        id = url.split(",")[0]
        if len(url.split(",")) == 2:
            ending = int(url.split(",")[1][1:-1])
        else:
            starting = int(url.split(",")[1][1:])
            ending = int(url.split(",")[2][1:-1])
    else:
        id = url[:-1]
        starting = 0
        ending = -1

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
    k = 0
    item = srt[k]
    start = item['start']
    end = start + item['duration']
    keep_adding = False
    keep_adding_correct_thresh = 1

    while k < len(srt):
        item = srt[k]

        if float(start) > ending and ending != -1:
            print("after ending")
            break
        if float(start) < starting:
            print("before begining")
            k += 1
            continue
        if contains_garabge(item['text']):
            print('contains_garabge')
            if not keep_adding:
                k += 1
                continue
            else:
                k += 1
                keep_adding = False
                keep_adding_correct_thresh = 1
                print("NO")
                continue
        
        if keep_adding:
            end += item['duration']
        else:
            start = item['start']
            end = start + item['duration']

        try:
            sub_clip = clip.subclip(start, end)
            sub_clip.write_audiofile(os.path.join('data', str(i).zfill(6) + ".wav"), ffmpeg_params=["-ac", "1", "-ar", "22050"])
        except Exception as e:
            print('Audio clip error:', e)
            k += 1
            keep_adding = False
            keep_adding_correct_thresh = 1
            continue

        wf = wave.open(os.path.join('data', str(i).zfill(6) + ".wav"), "rb")

        try:
            result = asyncio.run(get_vosk_prediction(wf))
            if result['text'] is None:
                k += 1
                keep_adding = False
                keep_adding_correct_thresh = 1
                continue
        except Exception as e:
            print('Vosk not running Error:', e)
            start_vosk()
            # k += 1
            continue

        if keep_adding:
            yt_words = final_result.split(" ") + item['text'].split(" ")
        else:
            yt_words = item['text'].split(" ")
        
        vosk_words = result['text'].split(" ")
        correct_word_count = 0
        incorrect_word_count = 0
        w_idx = 0
        end_idx = 0
        vosk_count = 0
        # print(yt_words)
        for v_idx, word in enumerate(vosk_words):
            if yt_words[w_idx] == word:
                correct_word_count += 1 
                w_idx += 1
                end_idx = v_idx
            elif correct_word_count < keep_adding_correct_thresh:
                end_idx = v_idx
                vosk_count += 1
                continue
            else:
                w_idx += 1
                incorrect_word_count += 1
            if incorrect_word_count > 1:
                break
            if w_idx >= len(yt_words):
                break
        
        final_result = " ".join(vosk_words[:vosk_count] + yt_words[:end_idx + 1])
        keep_adding = False
        keep_adding_correct_thresh = 1

        if correct_word_count == len(yt_words):
            k += 1
            if k < len(srt) and not contains_garabge(srt[k]['text']):
                keep_adding = True
                keep_adding_correct_thresh = len(vosk_words[:end_idx + 1])
                continue
        
        if correct_word_count <= 1:
            os.remove(os.path.join('data', str(i).zfill(6) + ".wav")) 
            print(" ".join(yt_words))
            print(result['text'])
            k += 1
            continue

        og_cut_off = start + result['result'][correct_word_count - 1]['end'] + 0.1
        sub_clip = clip.subclip(start, og_cut_off)
        total_sec += (og_cut_off) - start
        sub_clip.write_audiofile(os.path.join('data', str(i).zfill(6) + ".wav"), ffmpeg_params=["-ac", "1", "-ar", "22050"])

        print(" ".join(yt_words))
        print(result['text'])
        with open(os.path.join('data', str(i).zfill(6) + ".txt"), "w") as text_file:
            print("Final Result:", final_result)
            text_file.write(final_result)
        
        i += 1
        k += 1

        # j = 1
        # og_cut_off = item['start'] + item['duration']
        # if k + j < len(srt):
        #     next_start = srt[k + j]['start']
        
        #     # max clip length 11 seconds
        #     while next_start < og_cut_off and og_cut_off - item['start'] < 11 and not contains_garabge(srt[k + j]['text']):
        #         og_cut_off = next_start + srt[k + j]['duration']
        #         j += 1
        #         if k + j < len(srt):
        #             next_start = srt[k + j]['start']
        #         else:
        #             break
        #     temp_amount_to_increment_k = j

        #     try:
        #         sub_clip = clip.subclip(item['start'], og_cut_off)
        #         total_sec += (og_cut_off) - item['start']
        #         sub_clip.write_audiofile(os.path.join('data', str(i).zfill(6) + ".wav"), ffmpeg_params=["-ac", "1", "-ar", "22050"])
                
        #         wf = wave.open(os.path.join('data', str(i).zfill(6) + ".wav"), "rb")
        #         rec = KaldiRecognizer(model, wf.getframerate())
        #         rec.SetWords(True)
        #         rec.SetPartialWords(True)

        #         while True:
        #             data = wf.readframes(4000)
        #             if len(data) == 0:
        #                 break
        #             if rec.AcceptWaveform(data):
        #                 pass

        #         result = rec.FinalResult()
        #         result = json.loads(result)

        #         q = 1
        #         out_str = " ".join([word for word in item['text'].split(" ") if word != "" and word != "[Music]"]) + ' '
        #         while j > 1:
        #             out_str += " ".join([word for word in srt[k + q]['text'].split(" ") if word != "" and word != "[Music]"]) + " "
        #             q += 1
        #             j -= 1
                
        #         yt_words = out_str[:-1].split(" ")
        #         vosk_words = result['text'].split(" ")
        #         correct_word_count = 0
        #         for w_idx, word in enumerate(yt_words):
        #             if vosk_words[w_idx] == word:
        #                 correct_word_count += 1 
        #             else:
        #                 break
        #         if correct_word_count <= 1:
        #             os.remove(os.path.join('data', str(i).zfill(6) + ".wav")) 
        #             print(out_str)
        #             print(result['text'])
        #             i += 1
        #             k += temp_amount_to_increment_k
        #             continue

        #         final_result = " ".join(yt_words[:correct_word_count])
        #         og_cut_off = item['start'] + result['result'][correct_word_count - 1]['end'] + 0.1

        #         sub_clip = clip.subclip(item['start'], og_cut_off)
        #         total_sec += (og_cut_off) - item['start']
        #         sub_clip.write_audiofile(os.path.join('data', str(i).zfill(6) + ".wav"), ffmpeg_params=["-ac", "1", "-ar", "22050"])

        #         print(out_str)
        #         print(result['text'])
        #         with open(os.path.join('data', str(i).zfill(6) + ".txt"), "w") as text_file:
        #             print("Final Result:", final_result)
        #             text_file.write(final_result)
                
        #         i += 1
        #         k += temp_amount_to_increment_k
        #     except Exception as e:
        #         print(e)
        #         i += 1
        #         k += temp_amount_to_increment_k
        # else:
        #     try:
        #         sub_clip = clip.subclip(item['start'], og_cut_off)
        #         total_sec += (og_cut_off) - item['start']
        #         sub_clip.write_audiofile(os.path.join('data', str(i).zfill(6) + ".wav"), ffmpeg_params=["-ac", "1", "-ar", "22050"])
                
        #         wf = wave.open(os.path.join('data', str(i).zfill(6) + ".wav"), "rb")
        #         rec = KaldiRecognizer(model, wf.getframerate())
        #         rec.SetWords(True)
        #         rec.SetPartialWords(True)

        #         while True:
        #             data = wf.readframes(4000)
        #             if len(data) == 0:
        #                 break
        #             if rec.AcceptWaveform(data):
        #                 pass

        #         result = rec.FinalResult()
        #         result = json.loads(result)

        #         temp_amount_to_increment_k = j
        #         q = 1
        #         out_str = " ".join([word for word in item['text'].split(" ") if word != "" and word != "[Music]"]) + ' '
        #         while j > 1:
        #             out_str += " ".join([word for word in srt[k + q]['text'].split(" ") if word != "" and word != "[Music]"]) + " "
        #             q += 1
        #             j -= 1

        #         yt_words = out_str[:-1].split(" ")
        #         vosk_words = result['text'].split(" ")
        #         correct_word_count = 0
        #         for w_idx, word in enumerate(yt_words):
        #             if vosk_words[w_idx] == word:
        #                 correct_word_count += 1 
        #             else:
        #                 i += 1
        #                 k += temp_amount_to_increment_k
        #                 break
        #         if correct_word_count <= 1:
        #             os.remove(os.path.join('data', str(i).zfill(6) + ".wav"))
        #             print(out_str)
        #             print(result['text'])
        #             continue

        #         final_result = " ".join(yt_words[:correct_word_count])
        #         og_cut_off = item['start'] + result['result'][correct_word_count - 1]['end'] + 0.1

        #         sub_clip = clip.subclip(item['start'], og_cut_off)
        #         total_sec += (og_cut_off) - item['start']
        #         sub_clip.write_audiofile(os.path.join('data', str(i).zfill(6) + ".wav"), ffmpeg_params=["-ac", "1", "-ar", "22050"])

        #         print(out_str)
        #         print(result['text'])
        #         with open(os.path.join('data', str(i).zfill(6) + ".txt"), "w") as text_file:
        #             print("Final Result:", final_result)
        #             text_file.write(final_result)

        #         i += 1
        #         k += temp_amount_to_increment_k
        #     except Exception as e:
        #         print(e)
        #         i += 1
        #         k += temp_amount_to_increment_k

print("Total seconds saved: ", total_sec)
