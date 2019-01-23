import json, sys, os, pickle
from tqdm import tqdm

def preprocess_data(input_file):
    print("Reading input files..")

    with open(input_file) as f:
        data = json.load(f)

    abstracts = []
    mesh_terms = []

    for article in tqdm(data, desc="Grabbing abstracts and mesh terms"):
        abstracts.append("\n".join([x["text"] for x in article["abstract"]]))
        mesh_terms.append([tuple(x['mesh_id']) for x in article['mesh_list']])

    #print(abstracts[0])
    #print(mesh_terms[0])

    print("Dumping..")

    with open(os.path.splitext(input_file)[0] + "_abstracts.dump", "wb") as f:
        pickle.dump(abstracts, f)

    with open(os.path.splitext(input_file)[0] + "_mesh_terms.dump", "wb") as f:
        pickle.dump(mesh_terms, f)

if __name__ == '__main__':
    preprocess_data(sys.argv[1])