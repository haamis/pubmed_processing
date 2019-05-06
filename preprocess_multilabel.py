import json, sys, os, pickle
import numpy as np

from tqdm import tqdm

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer

from bert import tokenization

maxlen = 512

def tokenize(abstracts, maxlen=512):
    tokenizer = tokenization.FullTokenizer("../biobert_pubmed/vocab.txt", do_lower_case=False)
    ret_val = []
    for abstract in tqdm(abstracts, desc="Tokenizing abstracts"):
        abstract = ["[CLS]"] + tokenizer.tokenize(abstract)[0:maxlen-2] + ["[SEP]"]
        ret_val.append(abstract)
    return ret_val, tokenizer.vocab

def preprocess_data(input_file):
    print("Reading input files..")

    with open(input_file) as f:
        data = json.load(f)

    abstracts = []
    mesh_terms = []

    for article in tqdm(data, desc="Grabbing abstracts"):
        try:
            abstracts.append(article["title"] + '\n' + article["abstract"])
        except:
            import pdb; pdb.set_trace()

    for article in tqdm(data, desc="Grabbing mesh terms"):
        mesh_terms.append([part['mesh_id'] for part in article['mesh_list']])

    del data

    abstracts, vocab = tokenize(abstracts, maxlen=maxlen)

    print("Vectorizing..")
    token_vectors = np.asarray( [np.asarray( [vocab[token] for token in abstract] + [0] * (maxlen - len(abstract)) ) for abstract in abstracts] )
    print("Token_vectors shape:", token_vectors.shape)
    
    print("Binarizing labels..")
    mlb = MultiLabelBinarizer(sparse_output=True)
    labels = mlb.fit_transform(mesh_terms)
    labels = labels.astype('b')
    print("Labels shape:", labels.shape)

    abstracts_train, abstracts_test, labels_train, labels_test = train_test_split(abstracts, labels, test_size=0.1)

    print("Dumping..")

    with open(os.path.splitext(input_file)[0] + "_abstracts_train.dump", "wb") as f:
        pickle.dump(abstracts_train, f)
    
    with open(os.path.splitext(input_file)[0] + "_abstracts_test.dump", "wb") as f:
        pickle.dump(abstracts_test, f)
    
    with open(os.path.splitext(input_file)[0] + "_multilabels_train.dump", "wb") as f:
        pickle.dump(labels_train, f)
    
    with open(os.path.splitext(input_file)[0] + "_multilabels_test.dump", "wb") as f:
        pickle.dump(labels_test, f)

if __name__ == '__main__':
    preprocess_data(sys.argv[1])
