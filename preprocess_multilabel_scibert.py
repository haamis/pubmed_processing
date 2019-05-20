import json, sys, os, pickle, lzma
import numpy as np

from functools import partial

from multiprocessing import Pool

from tqdm import tqdm

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer

from bert import tokenization

MAXLEN = 512
PROCESSES = 20

def tokenize(abstracts, tokenizer, maxlen=512):
    ret_val = []
    for abstract in abstracts:
        abstract = ["[CLS]"] + tokenizer.tokenize(abstract)[0:maxlen-2] + ["[SEP]"]
        ret_val.append(abstract)
    return ret_val

def vectorize(abstracts, vocab, maxlen=512):
    ret_val = []
    for abstract in abstracts:
        ret_val.append(np.asarray( [vocab[token] for token in abstract] + [0] * (maxlen - len(abstract)) ))
    return np.asarray(ret_val)

def chunk_list(list, chunk_size):
    res = []
    for i in range(0, len(list), chunk_size):
        res.append(list[i:i+chunk_size])
    return res

def preprocess_data(input_file):
    
    # Create child processes before we load a bunch of data.
    with Pool(PROCESSES) as p:

        print("Reading input files..")

        with lzma.open(input_file, 'rt') as f:
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

        tokenizer = tokenization.FullTokenizer("../scibert_scivocab_uncased/vocab.txt", do_lower_case=False)

        # Prcess text in parallel by first dividing into chunks..
        abstracts_list = chunk_list(abstracts, len(abstracts)//PROCESSES)
        del abstracts

        # ..tokenizing and vectorizing those chunks..
        print("Tokenizing abstracts..")
        abstracts_list = p.map(partial(tokenize, tokenizer=tokenizer, maxlen=MAXLEN), abstracts_list)
        print("Vectorizing..")
        abstracts_list = p.map(partial(vectorize, vocab=tokenizer.vocab), abstracts_list)
    
    # Child processes terminated here.

    # ..and then combining the chunks back to a single list.
    abstracts = np.concatenate(abstracts_list)

    print("Token_vectors shape:", abstracts.shape)
    
    print("Binarizing labels..")
    mlb = MultiLabelBinarizer(sparse_output=True)
    labels = mlb.fit_transform(mesh_terms)
    labels = labels.astype('b')
    print("Labels shape:", labels.shape)

    abstracts_train, abstracts_test, labels_train, labels_test = train_test_split(abstracts, labels, test_size=0.1)

    # Using lzma because gzip refuses to compress files over 4GB.
    # Use compression level 0 to reduce processing time. 
    # This makes the compression take slightly less time than 
    # using the gzip python module with its default compression level (9).
    # The resulting file is still smaller than using gzip with compression level 9.
    with lzma.open(os.path.splitext(input_file)[0] + "_scibert_abstracts_train.dump.xz", "wb", preset=0) as f:
        pickle.dump(abstracts_train, f, protocol=4)
        # Use pickle protocol 4 to enable saving objects over 4GB.
    
    with lzma.open(os.path.splitext(input_file)[0] + "_scibert_abstracts_test.dump.xz", "wb", preset=0) as f:
        pickle.dump(abstracts_test, f, protocol=4)
    
    with lzma.open(os.path.splitext(input_file)[0] + "_scibert_multilabels_train.dump.xz", "wb", preset=0) as f:
        pickle.dump(labels_train, f, protocol=4)
    
    with lzma.open(os.path.splitext(input_file)[0] + "_scibert_multilabels_test.dump.xz", "wb", preset=0) as f:
        pickle.dump(labels_test, f, protocol=4)

if __name__ == '__main__':
    preprocess_data(sys.argv[1])
