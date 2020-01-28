import keras
import pickle
import argparse
import numpy as np
import pandas as pd
from numpy.random import seed
from tensorflow import set_random_seed
from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense, Embedding
from keras.layers import LSTM

seed(123)
set_random_seed(123)

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--namefile", default="data/annotated_names.tsv")
parser.add_argument("-m", "--model_name", default="LSTM")
parser.add_argument("-e", "--epochs", type=int, default=15)
args = parser.parse_args()

# Load objects from 04.featurize-names.py
filename = "models/%s_idx_dic.pkl" % args.model_name
idx_dic = pickle.load(open(filename, "rb"))
X_train = np.load("models/%s_X_train.npy" % args.model_name, allow_pickle=True)
y_train = np.load("models/%s_y_train.npy" % args.model_name, allow_pickle=True)
X_test = np.load("models/%s_X_test.npy" % args.model_name, allow_pickle=True)
y_test = np.load("models/%s_y_test.npy" % args.model_name, allow_pickle=True)


# max_features = num_words # 20000
num_words = len(idx_dic.keys())+1
print(num_words)
feature_len = 20
batch_size = 128

print(len(X_train), 'train sequences')
print(len(X_test), 'test sequences')

print('Pad sequences (samples x time)')
X_train = sequence.pad_sequences(X_train, maxlen=feature_len)
X_test = sequence.pad_sequences(X_test, maxlen=feature_len)
print('X_train shape:', X_train.shape)
print('X_test shape:', X_test.shape)

num_classes = np.max(y_train) + 1
print(num_classes, 'classes')

print('Convert class vector to binary class matrix '
      '(for use with categorical_crossentropy)')
y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)
print('y_train shape:', y_train.shape)
print('y_test shape:', y_test.shape)

print('Build model...')

model = Sequential()
model.add(Embedding(num_words, 32, input_length=feature_len))
model.add(LSTM(128, dropout=0.2, recurrent_dropout=0.2))
model.add(Dense(num_classes, activation='softmax'))

# try using different optimizers and different optimizer configs
model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

print(model.summary())

print('Train...')
model.fit(X_train, y_train, batch_size=batch_size, epochs=args.epochs,
          validation_split=0.1, verbose=2)
score, acc = model.evaluate(X_test, y_test,
                            batch_size=batch_size, verbose=2)
print('Test score:', score)
print('Test accuracy:', acc)

path = "models/%s.h5" % args.model_name
model.save(path)
