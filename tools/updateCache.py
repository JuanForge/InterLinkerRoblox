import pickle
from datetime import datetime, timezone
"""
with open("Cache.pkl", "rb") as fileIN, open("NewCache.pkl", "wb") as fileOUT:
    cache = pickle.load(fileIN)
    data = {"type:1": {}, "TotalTime": 0.0}
    data["TotalTime"] = cache["TotalTime"]
    for id, content in cache["type:1"].items():
        print("Updating", id)
        JSON = content.json()["data"][""]
        data["type:1"][id] = {"json": JSON, "updateTime": datetime.now(timezone.utc).date()}
    
    pickle.dump(data, fileOUT)

with open("NewCache.pkl", "rb") as f:
    restored = pickle.load(f)
    for id, content in restored["type:1"].items():
        print(id, content)
"""
with open("Cache.pkl", "rb") as fileIN, open("CacheV2.pkl", "wb") as fileOUT:
    cache = pickle.load(fileIN)
    newCache = {"type:1": {}, "TotalTime": 0.0}
    newCache["TotalTime"] = cache["TotalTime"]

    for key, value in cache["type:1"].items():
        key = int(key)
        # value = {'id': [list d'IDs]}
        ids = [int(x) for x in value['id'] if int(x) != -1]
        newCache["type:1"][key] = {}
        newCache["type:1"][key]["id"] = ids
        newCache["type:1"][key]["updateTime"] = value["updateTime"]
    pickle.dump(newCache, fileOUT)