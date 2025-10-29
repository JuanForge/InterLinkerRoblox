import os
import re
import sys
import time
import json
import queue
import yaspin
import random
import requests
import threading

import traceback

import itertools
import pickle
from yaspin import spinners
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

def log(msg: str):
    if True == True:
        sys.stdout.write(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC] {msg}\n")

def RequestsWapper(req: requests.Session, url: str, method: str = "GET", type = 0,
                   found_event: threading.Event = None, Cache: pickle = None, LockCache: threading.Lock = None) -> requests.Response:
    while not found_event.is_set():
        try:
            match = re.search(r"/users/(\d+)/friends", url)
            if match:
                user_id = match.group(1)
                with LockCache:
                    if user_id in Cache['type:1']:
                        log(f"Cache hit for user_id: {user_id}")
                        return Cache['type:1'][user_id]["id"]
                    else:
                        log(f"Cache miss for user_id: {user_id}")
            
            data = req.request(method=method, url=url)
            if data.status_code == 200:
                if type == 0:
                    JSON = {}
                    JSON = data.json()["data"]
                    #JSON["data"][0]['id']
                    #JSON[""]
                    with LockCache:
                        Cache['type:1'][user_id] = {
                            "id": [str(item["id"]) for item in JSON if item["id"] != -1],
                            "updateTime": datetime.now(timezone.utc).date()
                        }

                        #print(Cache['type:1'])
                    return [str(item["id"]) for item in JSON if item["id"] != -1]
            elif data.status_code == 429:
                log("Rate limit exceeded, sleeping X seconds...")
                time.sleep(random.uniform(8, 12))
                continue
        except Exception as e:
            print(f"Error RequestsWapper: {e}")
            print(traceback.format_exc())
            time.sleep(2)
            continue
    else:
        return None


def worker(IDuserFInd: str, Queue: queue.Queue,
            Set: set, lock: threading.Lock, found_event: threading.Event,
            result: dict, proxy, nombre: int, Cache: pickle, LockCache: threading.Lock) -> dict:
    rq = requests.Session()
    rq.proxies.update({
        "http": proxy,
        "https": proxy
    })
    while not found_event.is_set():
        try:
            userQueue = Queue.get(timeout=1)
        except Exception:
            continue

        with lock:
            if userQueue["id"] in Set:
                Queue.task_done()
                continue
            Set.add(userQueue["id"])
        try:
            #print(f"https://friends.roblox.com/v1/users/{userQueue['id']}/friends")
            #data = rq.get(f"https://friends.roblox.com/v1/users/{userQueue['id']}/friends")
            data = RequestsWapper(rq, f"https://friends.roblox.com/v1/users/{userQueue['id']}/friends", method="GET",
                                  type=0, found_event=found_event, Cache=Cache, LockCache=LockCache)
            if data is None:
                return True
            #print(data.json())
    
            for user in data:
                with lock:
                    nombre[0] += 1
                user = str(user)
                #user["id"] = str(5370327427)  # For testing purpose
                #sys.stdout.write(user["id"] + "\n")
                #print("\n" + user["id"] + "==" + IDuserFInd + "\n")
        
                if user == IDuserFInd:
                    found_event.set()
                    with lock:
                        result.update({
                            "status": True,
                            "username": "username",
                            "id": user,
                            "intermediate": userQueue["intermediate"] + [user]
                        })
                    return True
                  #return {"status": True, "username": user["name"], "id": user["id"], "intermediate": [user["name"]]}
                else:
                  Queue.put({"IDuserFInd": IDuserFInd, "id": user, "intermediate": userQueue["intermediate"] + [user]})
                  #iun = unit(rq, uernameFind, user["id"], Queue=Queue, Set=Set)
                  #if iun["status"]:
                  #    iun["intermediate"].append(user["name"])
                  #    return iun
                      #return {"status": True, "username": user["username"], "id": user["id"]}
        except Exception as e:
          print(f"Error: {e}")
          print(traceback.format_exc())
    return True
    #return {"status": False}



def main():
    thread = 8

    if os.path.exists("Cache.pkl"):
        Cache = pickle.load(open("Cache.pkl", "rb"))
    else:
        Cache = {"type:1": {}, "TotalTime": 0.0}
    LockCache = threading.Lock()

    uername = input("Username>> ")
    uernameFind = input("Username Find>> ")
    lock = threading.Lock()
    rq = requests.Session()
    Queue = queue.Queue(maxsize=0) # 2_000_000
    found_event = threading.Event()
    result = {"status": False}
    Set = set()
    nombre = [0]

    data = rq.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [uername], "excludeBannedUsers": False})
    data.raise_for_status()
    IDuser = data.json()["data"][0]["id"]
    IDuser = str(IDuser)
    print(f"IDuser ID: {IDuser}" + "\n")

    data = rq.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [uernameFind], "excludeBannedUsers": False})
    data.raise_for_status()
    IDuserFInd = data.json()["data"][0]["id"]
    IDuserFInd = str(IDuserFInd)
    print(f"IDuserFInd ID: {IDuserFInd}" + "\n")

    ThreadPool = ThreadPoolExecutor(max_workers=None)
    Queue.put({"IDuserFInd": IDuserFInd, "id": IDuser, "intermediate": [IDuser]})
    
    if os.path.exists("config.json"):
        proxy = itertools.cycle(json.loads(open("config.json").read())["proxy"])
    else:
        raise Exception("config.json not found")
    
    for _ in range(thread):
        ThreadPool.submit(worker, IDuserFInd, Queue, Set, lock, found_event, result, next(proxy), nombre, Cache, LockCache)
    print("Searching...")
    
    try:
        start_time = time.monotonic()
        with yaspin.yaspin(spinner=spinners.Spinners.material, text="Process en cours...", color="red", timer=True) as e:
            while not found_event.is_set():
                with lock:
                    e.text = f"Users scanned: {len(Set)} | Queue size: {Queue.qsize()}, Threads: {threading.active_count()}, nombre: {nombre}"
                time.sleep(1)
        print("Finished.")
    except KeyboardInterrupt:
        print("Interrupted by user")
        found_event.set()

    ThreadPool.shutdown(wait=True)
    print(result)
    with open("Cache.pkl", "wb") as f:
        Cache['TotalTime'] += (time.monotonic() - start_time)
        print(f"Total time life Cache: {Cache['TotalTime']:.2f} seconds")
        #print(Cache)
        pickle.dump(Cache, f)


    #if data['status']:
    #    print("->".join(data["intermediate"][::-1]))
    #    #print(f"Found: {user['username']} | ID: {user['id']}")

if __name__ == "__main__":
    main()