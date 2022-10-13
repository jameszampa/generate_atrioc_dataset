import os
import random
import numpy as np


def read_file(filename):
    with open(filename, 'r') as input_file:
        return input_file.read()


def shuffle_dataset(x, y=None):
    indices = list(range(len(x)))
    random.shuffle(indices)

    shuffled_x = []
    if y is None:
        for idx in indices:
            shuffled_x.append(x[idx])

        return shuffled_x
    else:
        shuffled_y = []
        for idx in indices:
            shuffled_x.append(x[idx])
            shuffled_y.append(y[idx])
        
        return np.asarray(shuffled_x), np.asarray(shuffled_y)


dir = 'data'
mel_dir = 'mels'

files = []
for file_name in os.listdir(dir):
    if file_name.endswith('.txt'):
        path = os.path.join(dir, file_name)
        files.append(path)

shuffled_files = shuffle_dataset(files)

train_files = shuffled_files[:int(len(shuffled_files) * 0.9)]
val_files = shuffled_files[int(len(shuffled_files) * 0.9):]

def write_annotations(filename, files):
    with open(filename, 'w', encoding='utf-8') as output_file:
        for file in files:
            text = read_file(file)
            text = text.replace('�', ' ')
            num_words = len(text.split(" "))
            if num_words < 6:
                continue
            file = file[:-4] + '.wav'
            if not os.path.exists(file):
                continue
            file_name = file.split(os.sep)[-1][:-4] + '.pt'
            mel_file = os.path.join(mel_dir, file_name)
            line = file + '|' + text + '\n'
            output_file.write(line)

write_annotations('ljs_audio_text_train_filelist.txt', train_files)
write_annotations('ljs_audio_text_val_filelist.txt', val_files)
