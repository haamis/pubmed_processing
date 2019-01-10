import sys, pickle
from tqdm import tqdm

def load_data(file_name):
    
    with open(file_name, "rb") as f:
        return pickle.load(f)

is_neuro = load_data("./" + sys.argv[1])

neuro_count = 0
for value in tqdm(is_neuro, desc="Counting.."):
    if value == 1:
        neuro_count += 1

print(neuro_count, "/", len(is_neuro))
print( (neuro_count / len(is_neuro)) * 100, "%")