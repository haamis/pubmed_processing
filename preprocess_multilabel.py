import json, sys, os, pickle, lzma
import numpy as np

from functools import partial

from multiprocessing import Pool

from tqdm import tqdm

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer

from bert import tokenization

maxlen = 512
PROCESSES = 20

def tokenize(abstract, tokenizer, maxlen=512):
    return ["[CLS]"] + tokenizer.tokenize(abstract)[0:maxlen-2] + ["[SEP]"]

def vectorize(abstract, vocab, maxlen=512):
    return np.asarray( [vocab[token] for token in abstract] + [0] * (maxlen - len(abstract)) )

def preprocess_data(input_file):
    
    # Create child processes before we load a bunch of data.
    with Pool(PROCESSES) as p:

        print("Reading input files..")

        with lzma.open(input_file, 'rt') as f:
            data = json.load(f)

        abstracts = []
        mesh_terms = []

        for article in tqdm(data, desc="Grabbing abstracts"):
            abstracts.append(article["title"] + '\n' + article["journal"] + '\n' + article["abstract"])

        for article in tqdm(data, desc="Grabbing mesh terms"):
            mesh_terms.append([part['mesh_id'] for part in article['mesh_list']])

        del data

        tokenizer = tokenization.FullTokenizer("../biobert_pubmed/vocab.txt", do_lower_case=False)

        print("Tokenizing..")
        abstracts = p.map(partial(tokenize, tokenizer=tokenizer), abstracts)#, chunksize=500)
        print("Vectorizing..")
        abstracts = p.map(partial(vectorize, vocab=tokenizer.vocab), abstracts)#, chunksize=500)
        # Child processes terminated here.

    abstracts = np.asarray(abstracts)
    
    print("Token_vectors shape:", abstracts.shape)
    
    print("Binarizing labels..")
    mlb = MultiLabelBinarizer(sparse_output=True)
    labels = mlb.fit_transform(mesh_terms)
    labels = labels.astype('b')
    print("Labels shape:", labels.shape)

    # Save list of labels.
    with open(os.path.splitext(input_file)[0] + "_class_labels.txt", "wt") as f:
        json.dump(list(mlb.classes_), f)

    abstracts_train, abstracts_test, labels_train, labels_test = train_test_split(abstracts, labels, test_size=0.1)

    # Use compression level 0 with lzma to reduce processing time. 
    # This makes the compression take slightly less time than 
    # using the gzip python module with its default compression level (9).
    # The resulting file is still smaller than using gzip with compression level 9.
    with lzma.open(os.path.splitext(input_file)[0] + "_abstracts_train.dump.xz", "wb", preset=0) as f:
        pickle.dump(abstracts_train, f, protocol=4)
        # Use pickle protocol 4 to enable saving objects over 4GB.
    
    with lzma.open(os.path.splitext(input_file)[0] + "_abstracts_test.dump.xz", "wb", preset=0) as f:
        pickle.dump(abstracts_test, f, protocol=4)
    
    with lzma.open(os.path.splitext(input_file)[0] + "_multilabels_train.dump.xz", "wb", preset=0) as f:
        pickle.dump(labels_train, f, protocol=4)
    
    with lzma.open(os.path.splitext(input_file)[0] + "_multilabels_test.dump.xz", "wb", preset=0) as f:
        pickle.dump(labels_test, f, protocol=4)

if __name__ == '__main__':
    preprocess_data(sys.argv[1])
