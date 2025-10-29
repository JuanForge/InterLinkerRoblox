import json
import pickle

with open("Cache.pkl", "rb") as f, open("Cache.json", "w") as out:
    Cache = pickle.load(f)
    json.dump(Cache, out, indent=4, default=str)