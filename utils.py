import numpy as np

iscb_diversity_commit="0cf4baa0a7456603a7d73482aae0afd61e674526"

def get_index_dic(vocab, a):

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
        except KeyError:
            idx = 0.
        wi.append(idx)
    return wi


def featurize_data(names_list, ngram, index_dic):

    feat_list = []
    for full_name in names_list:
        feats = find_ngrams(full_name, ngram, index_dic)
        feat_list.append(np.array(feats))
    return feat_list
