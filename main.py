import sys
import time
import json
import queue
import yaspin
import random
import requests
import threading

import itertools

from yaspin import spinners
from concurrent.futures import ThreadPoolExecutor

def worker(IDuserFInd: str, Queue: queue.Queue,
            Set: set, lock: threading.Lock, found_event: threading.Event, result: dict, proxy, nombre: int) -> dict:
    rq = requests.Session()
    rq.proxies.update({
        "http": proxy,
        "https": proxy
    })
    print(rq.proxies)
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
            print(f"https://friends.roblox.com/v1/users/{userQueue['id']}/friends")
            data = rq.get(f"https://friends.roblox.com/v1/users/{userQueue['id']}/friends")
            #print(data.json())
            time.sleep(random.uniform(2, 4))
    
            for user in data.json()["data"]:
                with lock:
                    nombre[0] += 1
                user["id"] = str(user["id"])
                sys.stdout.write(user["id"] + "\n")
        
                if user["id"] == IDuserFInd:
                    found_event.set()
                    with lock:
                        result.update({
                            "status": True,
                            "username": user["name"],
                            "id": user["id"],
                            "intermediate": userQueue["intermediate"] + [user["name"]]
                        })
                    return True
                  #return {"status": True, "username": user["name"], "id": user["id"], "intermediate": [user["name"]]}
                else:
                  Queue.put({"IDuserFInd": IDuserFInd, "id": user["id"], "intermediate": userQueue["intermediate"] + [user["name"]]})
                  #iun = unit(rq, uernameFind, user["id"], Queue=Queue, Set=Set)
                  #if iun["status"]:
                  #    iun["intermediate"].append(user["name"])
                  #    return iun
                      #return {"status": True, "username": user["username"], "id": user["id"]}
        except Exception as e:
          print(f"Error: {e}")
    return True
    #return {"status": False}



def main():
    thread = 8

    uername = input("Username>> ")
    uernameFind = input("Username Find>> ")
    lock = threading.Lock()
    rq = requests.Session()
    Queue = queue.Queue(maxsize=2_000_000)
    found_event = threading.Event()
    result = {"status": False}
    Set = set()
    nombre = [0]

    data = rq.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [uername], "excludeBannedUsers": False})
    IDuser = data.json()["data"][0]["id"]
    print(f"IDuser ID: {IDuser}" + "\n")

    data = rq.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [uernameFind], "excludeBannedUsers": False})
    IDuserFInd = data.json()["data"][0]["id"]
    print(f"IDuserFInd ID: {IDuserFInd}" + "\n")

    ThreadPool = ThreadPoolExecutor(max_workers=None)
    Queue.put({"IDuserFInd": IDuserFInd, "id": IDuser, "intermediate": [uername]})
    
    proxy = itertools.cycle(json.loads(open("config.json").read())["proxy"])
    for _ in range(thread):
        ThreadPool.submit(worker, IDuserFInd, Queue, Set, lock, found_event, result, next(proxy), nombre)
    print("Searching...")
    
    with yaspin.yaspin(spinner=spinners.Spinners.material, text="Process en cours...", color="red", timer=True) as e:
        while not found_event.is_set():
            e.text = f"Users scanned: {len(Set)} | Queue size: {Queue.qsize()}, Threads: {threading.active_count()}, nombre: {nombre}"
            time.sleep(1)
    
    print("Found!")
    print("Found!")
    ThreadPool.shutdown(wait=True)
    print(result)
    #data = worker(rq, uernameFind, IDuser, Queue=Queue, Set=Set, lock=lock, found_event=found_event, result=result)

    #if data['status']:
    #    print("->".join(data["intermediate"][::-1]))
    #    #print(f"Found: {user['username']} | ID: {user['id']}")

if __name__ == "__main__":
    main()