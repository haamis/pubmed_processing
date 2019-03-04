import json, sys, os, pickle
from tqdm import tqdm
from nltk import tokenize

def preprocess_data(input_file):
    print("Reading input files..")

    with open(input_file) as f:
        data = json.load(f)

    abstracts = []
    mesh_terms = []

    for article in tqdm(data, desc="Grabbing abstracts and mesh terms"):
        abstract = "\n".join( [ part["text"] for part in article["abstract"] ] )
        for sentence in tokenize.sent_tokenize(abstract):
            abstracts.append(sentence)
            mesh_terms.append([part['mesh_id'] for part in article['mesh_list']])

    print("Dumping abstracts..")

    with open(os.path.splitext(input_file)[0] + "_sentence_abstracts.dump", "wb") as f:
        pickle.dump(abstracts, f)     

    print("Dumping mesh terms..")

    with open(os.path.splitext(input_file)[0] + "_sentence_mesh_terms.dump", "wb") as f:
        pickle.dump(mesh_terms, f)

if __name__ == '__main__':
    preprocess_data(sys.argv[1])