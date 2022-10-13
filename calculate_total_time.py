import os

total_seconds = 0
url_file = "urls.txt"

with open(url_file, "r") as url:
    url_lines = url.readlines()

for line in url_lines:
    split_line = line.split(",")
    youtube_id = split_line[0]
    if len(split_line) == 2:
        ending_point = int(split_line[1][1:-1])
        if ending_point == -1:
            continue
        total_seconds += ending_point
    elif len(split_line) == 3:
        starting_point = int(split_line[1][1:])
        ending_point = int(split_line[1][1:-1])
        total_seconds += ending_point - starting_point
print((total_seconds / 60) / 60)