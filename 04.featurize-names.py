import utils
import pickle
import argparse
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--namefile", default="data/annotated_names.tsv")
parser.add_argument("-l", "--ngrams", type=int, default=3)
parser.add_argument("-m", "--model_name", default="LSTM")
args = parser.parse_args()

sdf = pd.read_csv(args.namefile, sep='\t', engine='python')
print(sdf.head)
sdf.dropna(subset=['name_first', 'name_last'], inplace=True)

sdf['name_first'] = sdf.name_first.str.title()
sdf['name_last'] = sdf.name_last.str.title()

print(sdf)

sdf.groupby('ethnicity').agg({'name_first': 'count'})

# concat last name and first name
sdf['name_last_name_first'] = sdf['name_last'] + ' ' + sdf['name_first']

# build n-gram list
NGRAMS = args.ngrams
vect = CountVectorizer(analyzer='char', max_df=.3, min_df=3, ngram_range=(NGRAMS, NGRAMS), lowercase=False)
a = vect.fit_transform(sdf.name_last_name_first)
vocab = vect.vocabulary_

idx_dic, words_list = utils.get_index_dic(vocab, a)
filename="models/"+args.model_name+"_idx_dic.pkl"
f = open(filename, "wb")
pickle.dump(idx_dic, f)
f.close()

print('generated indexes')

sdf['name_last_name_first'] = sdf['name_last'] + ' ' + sdf['name_first']
X = utils.featurize_data(sdf['name_last_name_first'], NGRAMS, idx_dic)

# build X from index of n-gram sequence
#X = np.array(sdf.name_last_name_first.apply(lambda c: find_ngrams(c, NGRAMS)))
print('built X')
# check max/avg feature

X_len = []
for x in X:
    X_len.append(len(x))

max_feature_len = max(X_len)
avg_feature_len = int(np.mean(X_len))

print("Max feature len = %d, Avg. jfeature len = %d" % (max_feature_len, avg_feature_len))
y = np.array(sdf.ethnicity.astype('category').cat.codes)
print(sdf.ethnicity.astype('category'))
categories=pd.DataFrame(sdf.ethnicity.astype('category').cat.categories)
categories.to_csv('models/%s_categories.txt'%args.model_name, sep="\t", index=False, header=None)

# Split train and test dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=21, stratify=y)

np.save('models/%s_X_train.npy'%args.model_name,X_train)
np.save('models/%s_y_train.npy'%args.model_name,y_train)
np.save('models/%s_X_test.npy'%args.model_name,X_test)
np.save('models/%s_y_test.npy'%args.model_name,y_test)
