import pickle
import argparse
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report,confusion_matrix

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--namefile", default="data/annotated_names.tsv")
parser.add_argument("-l", "--ngrams", default=3)
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

def get_index_dic(vocab):

    words = []
    for b in vocab:
        c = vocab[b]
        words.append((a[:, c].sum(), b))
    words = sorted(words, reverse=True)
    words_list = [w[1] for w in words]
    num_words = len(words_list)
    print("num_words = %d"% num_words)
    idx_dic = {}
    for i in range(len(words_list)):
        word = words_list[i]
        idx_dic[word] = i + 1
    return idx_dic, words_list


def find_ngrams(text, n, idx_dic):
    a = zip(*[text[i:] for i in range(n)])
    wi = []
    for i in a:
        w = ''.join(i)
        try:
            idx = float(idx_dic[w])
        except:
            idx = 0.
        wi.append(idx)
    return wi


def featurize_data(names_list, ngram, index_dic):

    feat_list = []
    for full_name in names_list:
        feats = find_ngrams(full_name, ngram, idx_dic)
        feat_list.append(np.array(feats))
    #idx_dic = get_index_dic(vocab)
    #X = np.array(names_list.apply(lambda c: find_ngrams(c, NGRAMS, index_dic)))
    return feat_list


idx_dic, words_list = get_index_dic(vocab)
filename="models/"+args.model_name+"_idx_dic.pkl"
f = open(filename, "wb")
pickle.dump(idx_dic, f)
f.close()

print('generated indexes')

sdf['name_last_name_first'] = sdf['name_last'] + ' ' + sdf['name_first']
X = featurize_data(sdf['name_last_name_first'], NGRAMS, idx_dic)

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

# Split train and test dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=21, stratify=y)

np.save('models/%s_X_train.npy'%args.model_name,X_train)
np.save('models/%s_y_train.npy'%args.model_name,y_train)
np.save('models/%s_X_test.npy'%args.model_name,X_test)
np.save('models/%s_y_test.npy'%args.model_name,y_test)
