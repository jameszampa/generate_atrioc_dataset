# This is more for fun than a puzzle
# 
# Find some text, you could download a book from project gutenberg, or r you could dump 
# all of the code in this project into one text file with 'cat ../../**/*.py > code.txt'
# 
# Next run this character-based GRU with char-gen.py some-text-file.txt
# If you are on a GPU you should use CuDNNGRU in place of GRU
# 
# See if you can get interesting results!  Play with the number of hidden nodes
# and try other RNN structures.  Modifying the diversity number doesn't affect
# the model but can lead to different output.
#
# This model loads all of the data into memory, and that will be huge (why?).
# Another fun project would be to use fit_generator to process a larger dataset.

import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import GRU
import numpy as np
import random
import sys
import io
import argparse


hidden_nodes = 128
batch_size = 256
file = 'dataset.txt'
maxlen = 2000
step = 1

# Only load first 100k charcters because we're not using memory efficiently
text = io.open(file, encoding='utf-8').read()
chars = sorted(list(set(text)))

char_indices = dict((c, i) for i, c in enumerate(chars))
indices_char = dict((i, c) for i, c in enumerate(chars))

# build a sequence for every <config.step>-th character in the text

sentences = []
next_chars = []
for i in range(0, len(text) - maxlen, step):
    sentences.append(text[i: i + maxlen])
    next_chars.append(text[i + maxlen])

# build up one-hot encoded input x and output y where x is a character
# in the text y is the next character in the text

x = np.zeros((len(sentences), maxlen, len(chars)), dtype=np.bool)
y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
for i, sentence in enumerate(sentences):
    for t, char in enumerate(sentence):
        x[i, t, char_indices[char]] = 1
    y[i, char_indices[next_chars[i]]] = 1

model = Sequential()
model.add(GRU(hidden_nodes, input_shape=(maxlen, len(chars))))
model.add(Dense(len(chars), activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer="rmsprop")


def sample(preds, temperature=1.0):
    # helper function to sample an index from a probability array
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)


class SampleText(keras.callbacks.Callback):
    def on_epoch_end(self, batch, logs={}):
        start_index = random.randint(0, len(text) - maxlen - 1)

        for diversity in [0.5, 1.2]:
            print()
            print('----- diversity:', diversity)

            generated = ''
            sentence = text[start_index: start_index + maxlen]
            generated += sentence
            print('----- Generating with seed: "' + sentence + '"')
            sys.stdout.write(generated)

            for i in range(200):
                x_pred = np.zeros((1, maxlen, len(chars)))
                for t, char in enumerate(sentence):
                    x_pred[0, t, char_indices[char]] = 1.

                preds = model.predict(x_pred, verbose=0)[0]
                next_index = sample(preds, diversity)
                next_char = indices_char[next_index]

                generated += next_char
                sentence = sentence[1:] + next_char

                sys.stdout.write(next_char)
                sys.stdout.flush()
            print()


model.fit(x, y, batch_size=batch_size,
          epochs=100, callbacks=[SampleText()])