import json, csv, sys

print("Reading input files..")

mesh_ids = []

print("Reading mesh data..")
# Rest are read from csv files that are queried from NLM.
for mesh_file in sys.argv[1:-1]:
    with open("./" + mesh_file) as f:
        csvreader = csv.reader(f)
        next(csvreader) # Skip first entry, it is the name of the field e.g. 'descriptor'
        for entry in csvreader:
            if entry not in mesh_ids:
                mesh_ids.append(entry[0].split("/")[-1])

print("Dumping mesh ids..")

with open(sys.argv[-1], "wt") as f:
    json.dump(mesh_ids, f)