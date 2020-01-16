import pickle
import argparse
import numpy as np
import pandas as pd
from keras.models import load_model
from keras.preprocessing import sequence


parser = argparse.ArgumentParser()
parser.add_argument("-n", "--namefile", default="data/annotated_names.tsv")
parser.add_argument("-m", "--model_name", default="LSTM")
parser.add_argument("-e", "--epochs", type=int, default=15)
args = parser.parse_args()


def find_ngrams(text, n, idx_dic):

    a = zip(*[text[i:] for i in range(n)])
    wi = []
    for i in a:
        w = ''.join(i)
        try:
            idx = float(idx_dic[w])
        except KeyError:
            idx = 0.
        wi.append(idx)
    return wi


def featurize_data(names_list, ngram, index_dic):

    feat_list = []
    for full_name in names_list:
        feats = find_ngrams(full_name, ngram, idx_dic)
        feat_list.append(np.array(feats))
    return feat_list


ngram = 3
# load the model
model = load_model("models/%s.h5" % args.model_name)

df = pd.read_csv('exploratory/ISMB_Keynotes.txt', sep='\t')
df.dropna(subset=['fore_name', 'last_name'], inplace=True)
sdf = df
sdf['name_last_name_first'] = sdf['last_name'] + ' ' + sdf['fore_name']

filename = "models/" + args.model_name + "_idx_dic.pkl"
idx_dic = pickle.load(open(filename, "rb"))
ismb_names_list = sdf['name_last_name_first']

# should get a list of strings with format: firstName + ' ' + lastName
X_ismb = featurize_data(ismb_names_list, 3, idx_dic)
X_ismb = sequence.pad_sequences(X_ismb, maxlen=20)
y_ismb_pred = model.predict_classes(X_ismb, verbose=2)

print(y_ismb_pred)
