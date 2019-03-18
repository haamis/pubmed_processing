import csv, json, sys
from tqdm import tqdm

with open(sys.argv[1], "rt") as f:
        articles = json.load(f)

with open(sys.argv[2], "wt") as f:
    csv_writer = csv.writer(f)
    for article in tqdm(articles, desc="JSON to CSV"):
        labels = [mesh["mesh_id"] for mesh in article["mesh_list"]]
        abstract = [part["text"] for part in article["abstract"]]
        csv_writer.writerow([labels, abstract])