from selenium import webdriver
import pyautogui
import time

with open('urls3.txt', 'r') as input_file:
    lines = input_file.readlines()

yt =  webdriver.Chrome()
with open("titles3.txt", 'w') as output_file:
    for line in lines:
        yt.get(line[:-1])
        print(yt.title)
        try:
            output_file.write(yt.title)
            output_file.write("\n")
        except:
            output_file.write('Jeff Bezos - YouTube')
            output_file.write("\n")
yt.close()
