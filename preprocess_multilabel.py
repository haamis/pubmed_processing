import json, sys, os, pickle, time
from tqdm import tqdm

def preprocess_data(input_file):
    print("Reading input files..")

    with open(input_file) as f:
        data = json.load(f)

    abstracts = []
    mesh_terms = []

    #print(data[1])

    print("Grabbing abstracts..")

    for article in tqdm(data, desc="Grabbing abstracts"):
        # all_parts = []
        # for part in article["abstract"]:
        #     all_parts.append(part["text"])
        # abstracts.append("\n".join(all_parts))
        #time.sleep(0.01)
        abstracts.append("\n".join( [ part["text"] for part in article["abstract"] ] ))

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