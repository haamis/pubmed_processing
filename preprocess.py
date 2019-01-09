import json, re, sys, os, pickle, csv
from tqdm import tqdm

def preprocess_data(input_file, mesh_file):
    print("Reading input files..")

    with open(input_file) as f:
        data = json.load(f)

    mesh_ids = []

    with open(mesh_file) as f:
        csvreader = csv.reader(f)
        for entry in csvreader:
            mesh_ids.append(entry[0].split("/")[-1])

    mesh_ids.pop(0)

    abstracts = []
    is_neuro = []

    # Neuroscience MeSH-terms.
    reg = re.compile(r"|".join([x for x in mesh_ids]))

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
    preprocess_data(*sys.argv[1:])