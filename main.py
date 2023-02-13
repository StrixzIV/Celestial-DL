import os
import time
import shutil
import zipfile
import pythainlp
import numpy as np

from tensorflow import keras

from loader import *

MAX_LENGTH = 20

model_version = get_model_version('./model')

data1 = load_json('./data/intents_th.json')
data2 = load_json('./data/intents_en.json')

label_encoder = load_label_encoder(f'./model/model_v{model_version}/label_encoder.pickle')
word_encoder = load_label_encoder(f'./model/model_v{model_version}/word_label_encoder.pickle')

data = data1['intents_th'] + data2['intents_en']
model = load_keras_model(f'./model/model_v{model_version}/chat_model')

def to_sequences(message) -> list[int]:
    msg = pythainlp.word_tokenize(message, keep_whitespace = False)
    return word_encoder.transform(msg)

while True:

    input_message = input('usr> ').lower()

    start = time.perf_counter()

    if input_message == 'quit':
        break
    
    try:

        sequence = to_sequences(input_message)
        print(sequence)
        
        result = model.predict(keras.preprocessing.sequence.pad_sequences([sequence], truncating = 'post', maxlen = MAX_LENGTH))
        print(np.argmax(result))

        tag = label_encoder.inverse_transform([np.argmax(result)])

        for i in data:
            if i['tag'] == tag:
                print(f'celestial: {np.random.choice(i["responses"])}')

    except ValueError as e:
        print('Unkown responses')
        print(e)

    end = time.perf_counter()

    elasped = start - end
    print(f'Time elasped: {round((end - start) * 1000, 4)} ms')