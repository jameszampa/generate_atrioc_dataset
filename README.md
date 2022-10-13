# generate_atrioc_dataset

This repository is for generating data in the style of the [LJ Speech Dataset](https://keithito.com/LJ-Speech-Dataset/)
from a list of YouTube video IDs. This example uses just chatting sections from [Atrioc's VOD channel](https://www.youtube.com/channel/UCEQg9lX9Y61J4U9Gck9QsWg), 
[Marketing Monday](https://www.youtube.com/watch?v=xh4hC5Hy2uk&list=PLrMS357ieiqSvFBzFAGsIE0uiopBxHI_-), 
and [Atrioc Stories](https://www.youtube.com/watch?v=S7pTeHN5dvc&list=PLrMS357ieiqQdW7aqDg6glVikAoaGMCbX) playlists to create a dataset for use with
[Tacotron2](https://github.com/NVIDIA/tacotron2) and [Waveglow](https://github.com/NVIDIA/waveglow)

# Creating the dataset

The first step was to create a list of YouTube video ids to parse through. I acomplished this mostly through `test4.py` which used 
pyautogui and selenium to manually click through the playlist and copy the URLs to a file. After the list of URLs is created I parsed them
into `urls_unique.txt` using `test7.py`. I know my naming convention isn't great here. Once the list of video ids is created I use `download_audio.py`
to download the audio from the videos. That will give you a bunch of files each being named its video id .mp3. I moved all those videos to a folder called raw_data
Once the audio is downloaded it needs to be annotated and split into clips. I started by just using YouTube caption data for the subtitles, see `make_clips.py`
`make_clips.py` will create clips from the youtube caption data and save .wav and .txt files.
