from selenium import webdriver
import pyautogui
import time

NUM_VIDEOS = 594
OUTPUT_FILE = 'urls4.txt'
sleep_time = 1

yt =  webdriver.Chrome()
yt.get('https://www.youtube.com/watch?v=zRXHH5Z3NAk&list=UUgv4dPk_qZNAbUW9WkuLPSA&index=486')

i = 486
with open(OUTPUT_FILE, "a") as output_file:
    output_file.write(yt.current_url)
    output_file.write("\n")
    while i < NUM_VIDEOS:
        time.sleep(sleep_time)
        pyautogui.click(x=175,y=675)
        print(yt.current_url)
        output_file.write(yt.current_url)
        output_file.write("\n")
        i += 1