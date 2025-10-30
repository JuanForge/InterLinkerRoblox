import pickle

Cache = {
    "123": {
        "id": set(["2691511840", "3610801211", "9780257198"]),
        "updateTime": "2025-10-29"
    }
}


with open("Cache.pkl", "wb") as f:
    pickle.dump(Cache, f)