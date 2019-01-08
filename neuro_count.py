import sys, pickle

def load_data(file_name):
    
    with open(file_name, "rb") as f:
        return pickle.load(f)

is_neuro = load_data("./" + sys.argv[1])

neuro_count = 0
for value in is_neuro:
    if value == "yes":
        neuro_count += 1

print(neuro_count, "/", len(is_neuro))
print( (neuro_count / len(is_neuro)) * 100, "%")