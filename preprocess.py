import json, re, sys, os, pickle
from tqdm import tqdm

def preprocess_data(input_file):
    print("Reading input file..")

    with open(input_file) as f:
        data = json.load(f)

    abstracts = []
    is_neuro = []

    # Neuroscience MeSH-terms.
    reg = re.compile(r"(D009420|D009457|D009474|D009422|D001520|D011579|D001523|D004191)")

    for article in tqdm(data, desc="Grabbing abstracts and mesh terms"):
        abstracts.append("\n".join([x["text"] for x in article["abstract"]]))
        is_neuro.append(0)
        for mesh_term in article["mesh_list"]:
            if reg.match(mesh_term["mesh_id"]):
                is_neuro[-1] = 1
                break

    print("Dumping..")

    with open(os.path.splitext(input_file)[0] + "_abstracts.dump", "wb") as f:
        pickle.dump(abstracts, f)

    with open(os.path.splitext(input_file)[0] + "_is_neuro.dump", "wb") as f:
        pickle.dump(is_neuro, f)

if __name__ == '__main__':
    preprocess_data(sys.argv[1])