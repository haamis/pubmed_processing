import json, csv, sys

from tqdm import tqdm

with open(sys.argv[1], "rt") as f:
    print("Reading json..")
    articles = json.load(f)
    #import pdb; pdb.set_trace()
    # BioASQ's training data json is silly if you ask me.
    articles = articles["articles"]

with open(sys.argv[2], "wt") as f:
    csv_writer = csv.writer(f)
    for article in tqdm(articles, desc="Dumping to CSV"):
        labels = [mesh for mesh in article["meshMajor"]]
        # If null, replace with empty string.
        abstract = " ".join((article["title"] or "", article["journal"] or "", article["abstractText"] or ""))
        csv_writer.writerow([labels, abstract])