import keras
import pickle
import argparse
import numpy as np
import pandas as pd
from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense, Embedding, Dropout, Activation
from keras.layers import LSTM
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D
from keras.models import load_model
from sklearn.metrics import classification_report, confusion_matrix


parser = argparse.ArgumentParser()
parser.add_argument("-n", "--namefile", default="data/annotated_names.tsv")
parser.add_argument("-m", "--model_name", default="LSTM")
parser.add_argument("-e", "--epochs", type=int, default=15)
args = parser.parse_args()

# Load objects from 04.featurize-names.py
filename = "models/" + args.model_name + "_idx_dic.pkl"
idx_dic = pickle.load(open(filename,"rb"))
X_train = np.load("models/" + args.model_name + "_X_train.npy", allow_pickle= True)
y_train = np.load("models/" + args.model_name + "_y_train.npy", allow_pickle= True)
X_test = np.load("models/" + args.model_name + "_X_test.npy", allow_pickle= True)
y_test = np.load("models/" + args.model_name + "_y_test.npy", allow_pickle= True)



#max_features = num_words # 20000
num_words = len(idx_dic.keys())+1
print(num_words)
feature_len = 20 # avg_feature_len # cut texts after this number of words (among top max_features most common words)
#batch_size = 32
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


sdf = pd.read_csv(args.namefile, sep="\t", low_memory=False)
print(sdf.head)
sdf.dropna(subset=['name_first', 'name_last'], inplace=True)

sdf['name_first'] = sdf.name_first.str.title()
sdf['name_last'] = sdf.name_last.str.title()

sdf.groupby('ethnicity').agg({'name_first': 'count'})

# concat last name and first name
sdf['name_last_name_first'] = sdf['name_last'] + ' ' + sdf['name_first']


y_pred = model.predict_classes(X_test, verbose=2)
p = model.predict_proba(X_test, verbose=2) # to predict probability
target_names = list(sdf.ethnicity.astype('category').cat.categories)
print(classification_report(np.argmax(y_test, axis=1), y_pred, target_names=target_names))
print(confusion_matrix(np.argmax(y_test, axis=1), y_pred))

path = "models/%s.h5"%args.model_name
model.save(path)
