import re

with open("urls4.txt", 'r') as input_file:
    lines = input_file.readlines()


video_dict = {}
video_dict['1'] = 'Tvfy21A2CeE'
for line in lines[1:]:
    print(line)
    match = re.search(r"https://www.youtube.com/watch\?v=([a-zA-Z0-9_-]+)&list=UUgv4dPk_qZNAbUW9WkuLPSA&index=([0-9]+)", line)
    print(match[1], match[2])
    video_dict[str(match[2])] = str(match[1])

for i in range(1, 70, 1):
    if not str(i) in video_dict.keys():
        print("missing: ", i) 

