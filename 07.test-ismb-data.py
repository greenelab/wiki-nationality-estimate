import sys
import utils
import pickle
import argparse
import requests
import numpy as np
import pandas as pd
from keras.models import load_model
from keras.preprocessing import sequence


parser = argparse.ArgumentParser()
parser.add_argument("-l", "--ngrams", type=int, default=3)
parser.add_argument("-m", "--model_name", default="LSTM")
args = parser.parse_args()

# Load model
model = load_model("models/%s.h5" % args.model_name)
filename = "models/" + args.model_name + "_idx_dic.pkl"
idx_dic = pickle.load(open(filename, "rb"))
categories = pd.read_csv("models/%s_categories.txt" % args.model_name, header=None)

# Get PubMed author data from iscb-diversity repo
df = pd.read_csv("https://github.com/greenelab/iscb-diversity/raw/%s/data/names/full-names.tsv.xz"%utils.iscb_diversity_commit, sep='\t')
sdf = df
pubmed_names_list = list(sdf['full_name'].drop_duplicates())

X_pubmed = utils.featurize_data(pubmed_names_list, args.ngrams, idx_dic)
X_pubmed = sequence.pad_sequences(X_pubmed, maxlen=20)
y_pubmed_pred = model.predict_proba(X_pubmed, verbose=2)
print("PubMed authors",np.mean(y_pubmed_pred, axis=0))
y_pubmed_prob = pd.DataFrame(y_pubmed_pred, columns=categories[0], index=pubmed_names_list)
y_pubmed_prob.to_csv("data/%s_results_authors.tsv" % args.model_name, sep='\t')


# Get ISMB keynote data from iscb-diversity repo
df = pd.read_csv("https://raw.githubusercontent.com/greenelab/iscb-diversity/%s/data/iscb/keynotes.tsv"%utils.iscb_diversity_commit, sep='\t')
sdf = df
ismb_names_list = list(sdf['full_name'].drop_duplicates())

# should get a list of strings with format: firstName + ' ' + lastName
X_ismb = utils.featurize_data(ismb_names_list, args.ngrams, idx_dic)
X_ismb = sequence.pad_sequences(X_ismb, maxlen=20)
y_ismb_pred = model.predict_proba(X_ismb, verbose=2)
print("ISMB keynotes",np.mean(y_ismb_pred, axis=0))
y_ismb_prob = pd.DataFrame(y_ismb_pred, columns=categories[0], index=ismb_names_list)

y_ismb_prob.to_csv("data/%s_results_keynotes.tsv" % args.model_name, sep='\t')
