import json
import pickle


def op(o):
    return str(o) + " (type: " + str(type(o)) + ")"

with open("CacheV2.pkl", "rb") as f, open("CacheV2.json", "w") as out:
    Cache = pickle.load(f)
    json.dump(Cache, out, indent=4, default=op)