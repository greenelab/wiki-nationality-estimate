import keras
import pickle
import argparse
import numpy as np
import pandas as pd
from keras.models import load_model
from keras.preprocessing import sequence
from sklearn.metrics import log_loss, roc_auc_score, confusion_matrix, classification_report
from sklearn.metrics import roc_curve, auc

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--ngrams", type=int, default=3)
parser.add_argument("-m", "--model_name", default="LSTM")
parser.add_argument("-n", "--namefile", default="data/annotated_names.tsv")
args = parser.parse_args()

# Load model
model = load_model("models/%s.h5" % args.model_name)
filename = "models/" + args.model_name + "_idx_dic.pkl"
idx_dic = pickle.load(open(filename, "rb"))
categories = list(pd.read_csv("models/%s_categories.txt" % args.model_name, header=None, names=['category']).category)
X_train = np.load("models/%s_X_train.npy" % args.model_name, allow_pickle=True)
y_train = np.load("models/%s_y_train.npy" % args.model_name, allow_pickle=True)
X_test = np.load("models/%s_X_test.npy" % args.model_name, allow_pickle=True)
y_test = np.load("models/%s_y_test.npy" % args.model_name, allow_pickle=True)


num_words = len(idx_dic.keys())+1
feature_len = 20
batch_size = 128


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


# Get PubMed author data from iscb-diversity repo
sdf = pd.read_csv(args.namefile, sep="\t", low_memory=False)
sdf.dropna(subset=['name'], inplace=True)

sdf['name'] = sdf.name.str.title()

sdf.groupby('ethnicity').agg({'name': 'count'})


y_pred = model.predict_classes(X_test, verbose=2)
y_prob = model.predict_proba(X_test, verbose=2)  # to predict probability
target_names = list(sdf.ethnicity.astype('category').cat.categories)
print("Log loss", log_loss(y_test, y_prob))

y_true = np.argmax(y_test, axis=1)
print("ROC/AUC", roc_auc_score(y_true, y_prob, multi_class='ovo'))
print("Classification report\n", classification_report(y_true, y_pred, target_names=target_names))
print("Confusion matrix\n", confusion_matrix(np.argmax(y_test, axis=1), y_pred))


# Compute ROC curve and ROC area for each class
roc_aucs = list()
roc_dfs = list()
for i in range(num_classes):
    fpr, tpr, threshold = roc_curve(y_test[:, i], y_prob[:, i])
    df = pd.DataFrame({'fpr': fpr, 'tpr': tpr, 'threshold': threshold})
    df['category'] = categories[i]
    roc_dfs.append(df)
    roc_aucs.append(auc(fpr, tpr))
roc_df = pd.concat(roc_dfs)
auroc_df = pd.DataFrame({'category': categories, 'roc_auc': roc_aucs})
roc_df.to_csv(f"models/{args.model_name}_roc_curves.tsv", sep="\t", index=False)
auroc_df.to_csv(f"models/{args.model_name}_auroc.tsv", sep="\t", index=False)
