import json, re, sys, os, pickle
from tqdm import tqdm

def preprocess_data(input_file, mesh_file):
    print("Reading input files..")

    with open(input_file) as f:
        data = json.load(f)

    print("Reading mesh data..")

    with open(mesh_file) as f:
        mesh_ids = set(json.load(f))

    reg_string = r"|".join([x for x in mesh_ids])

    reg = re.compile(reg_string)

    abstracts = []
    is_neuro = []

    for article in tqdm(data, desc="Grabbing abstracts and mesh terms"):
        abstract = []
        abstract.append("\n".join([x["text"] for x in article["abstract"]]))
        abstract.append(article["pubmed_id"])
        abstracts.append(abstract)
        is_neuro.append(0)
        for mesh_term in article["mesh_list"]:
            if reg.match(mesh_term["mesh_id"]):
                is_neuro[-1] = 1
                break

    print("Dumping..")

    with open(os.path.splitext(input_file)[0] + "_abstracts_with_id.dump", "wb") as f:
        pickle.dump(abstracts, f)

    with open(os.path.splitext(input_file)[0] + "_is_neuro.dump", "wb") as f:
        pickle.dump(is_neuro, f)

if __name__ == '__main__':
    preprocess_data(sys.argv[1], sys.argv[2])