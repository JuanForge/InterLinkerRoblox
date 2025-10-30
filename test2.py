import pickle
with open("Cache.pkl", "rb") as f:
    Cache_loaded = pickle.load(f)

print(type(Cache_loaded["123"]["id"]))