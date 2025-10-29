import pickle
from datetime import datetime, timezone

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