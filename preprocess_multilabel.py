import json, sys, os, pickle
from tqdm import tqdm

def preprocess_data(input_file):
    print("Reading input files..")

    with open(input_file) as f:
        data = json.load(f)

    abstracts = []
    mesh_terms = []

    print("Grabbing abstracts..")

    for article in tqdm(data, desc="Grabbing abstracts"):
        try:
            abstracts.append("\n".join( [ part["text"] for part in article["abstract"] ] ))
        except:
            import pdb; pdb.set_trace()

    print("Dumping abstracts..")

    with open(os.path.splitext(input_file)[0] + "_abstracts.dump", "wb") as f:
        pickle.dump(abstracts, f)
    del abstracts


    for article in tqdm(data, desc="Grabbing mesh terms"):
        mesh_terms.append([part['mesh_id'] for part in article['mesh_list']])

    print("Dumping mesh terms..")

    with open(os.path.splitext(input_file)[0] + "_mesh_terms.dump", "wb") as f:
        pickle.dump(mesh_terms, f)

if __name__ == '__main__':
    preprocess_data(sys.argv[1])