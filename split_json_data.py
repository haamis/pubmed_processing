import json
import sys
import random

print("Reading input file..")

with open("./" + sys.argv[1]) as f:
    data = json.load(f)

print("Shuffling..")

random.shuffle(data)

print("Dumping..")

with open("./" + sys.argv[2], "wt") as f:
    json.dump(data[0:len(data)//10], f, indent=2, sort_keys=True)