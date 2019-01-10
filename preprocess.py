import json, re, sys, os, pickle, csv
from tqdm import tqdm

def preprocess_data(input_file, *mesh_files):
    print("Reading input files..")

    with open(input_file) as f:
        data = json.load(f)

    # Set of MeSH-term UIDs initialized with some values.
    mesh_ids = set(["D009420", "D009422", "D001520", "D011579", "D001523", "D004191"])

    print("Reading mesh data..")
    # Rest are read from csv files that are queried from NLM.
    for mesh_file in mesh_files:
        with open(mesh_file) as f:
            csvreader = csv.reader(f)
            next(csvreader) # Skip first entry, it is the name of the field e.g. 'descriptor'
            for entry in csvreader:
                mesh_ids.add(entry[0].split("/")[-1])

    reg_string = r"|".join([x for x in mesh_ids])

    reg = re.compile(reg_string)

    abstracts = []
    is_neuro = []

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
    preprocess_data(sys.argv[1], *sys.argv[2:])