import os
import pickle
import shutil
import pythainlp
import numpy as np
import pandas as pd

from sklearn.preprocessing import LabelEncoder

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, GlobalAveragePooling1D
from tensorflow.keras.preprocessing.sequence import pad_sequences

from utils.loader import get_model_version

model_version = get_model_version('./model')

data_th = pd.read_json('./data/intents_th.json')
data_en = pd.read_json('./data/intents_en.json')

data = list(data_th['intents_th']) + list(data_en['intents_en'])

training_sentences = []
training_labels = []
labels = []
responses = []

for intent in data:
    
    for pattern in intent['patterns']:
        training_sentences.append(pattern.lower())
        training_labels.append(intent['tag'])
    
    responses.append(intent['responses'])
    
    if intent['tag'] not in labels:
        labels.append(intent['tag'])
        
num_classes = len(labels)

wordlist = [pythainlp.word_tokenize(seq, keep_whitespace = False) for seq in training_sentences]
wordset = list(set([j for i in wordlist for j in i]))

label_encoder = LabelEncoder()
label_encoder.fit(training_labels)

training_labels = label_encoder.transform(training_labels)

word_label_encoder = LabelEncoder()
word_label_encoder.fit(wordset)

encoded_sentences = pad_sequences([word_label_encoder.transform(wl) for wl in wordlist], truncating = 'post', maxlen = 20)

max_length = 20
model = Sequential()

model.add(Embedding(len(wordset), 16, input_length = 20))
model.add(GlobalAveragePooling1D())
model.add(Dense(16, activation = 'relu'))
model.add(Dense(16, activation = 'relu'))
model.add(Dense(16, activation = 'relu'))
model.add(Dense(num_classes, activation = 'softmax'))

model.compile(loss = 'sparse_categorical_crossentropy', optimizer = 'adam', metrics = ['accuracy'])
model.fit(encoded_sentences, np.array(training_labels), epochs = 800)

new_version = model_version + 1

os.makedirs(f'./model/model_v{new_version}')

model.save(f'./model/model_v{new_version}/chat_model')

with open(f'./model/model_v{new_version}/label_encoder.pickle', 'wb') as ecn_file:
    pickle.dump(label_encoder, ecn_file, protocol = pickle.HIGHEST_PROTOCOL)

with open(f'./model/model_v{new_version}/word_label_encoder.pickle', 'wb') as ecn_file:
    pickle.dump(word_label_encoder, ecn_file, protocol = pickle.HIGHEST_PROTOCOL)
    
out = pd.concat([data_en, data_th], axis = 1)
out.to_parquet(f'./model/model_v{new_version}/intents.parquet')

shutil.make_archive(f'model/model_v{new_version}', 'zip', f'./model/model_v{new_version}')