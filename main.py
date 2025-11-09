import os
import re
import sys
import time
import json
import queue
import orjson
import random
import pickle
import argparse
import requests
import itertools
import threading
import traceback

import zstandard as zstd
from pympler import asizeof
from yaspin import yaspin, Spinner
from yaspin.spinners import Spinners
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

def RequestsWapper(proxy: itertools, url: str, method: str = "GET", type = 0,
                   found_event: threading.Event = None, Cache: pickle = None, LockCache: threading.Lock = None,
                   log = lambda x: None, lockNombre: threading.Lock = None, nombre=None, user_id: int = None, lock: threading.Lock = None) -> requests.Response:
    while not found_event.is_set(): # while True:
        try:
            with lock:
                req = next(proxy)
            
            
            with LockCache:
                if user_id in Cache['type:1']:
                    log(f"\033[0;32mCache hit for user_id: {user_id}\033[0m")
                    return Cache['type:1'][user_id]["id"]
                else:
                    log(f"\033[0;31mCache miss for user_id: {user_id}\033[0m")
            
            with req["lock"]:
                #print(f"\033[F\rUsing proxy: {req['rq'].proxies}")
                data = req["rq"].request(method=method, url=url)
            
            if data.status_code == 200:
                if type == 0:
                    JSON = {}
                    JSON = data.json()["data"]
                    #JSON["data"][0]['id']
                    #JSON[""]
                    # ids = [str(item["id"]) for item in JSON if item["id"] != -1]
                    ids = [int(item["id"]) for item in JSON if item["id"] != -1]
                    with lockNombre:
                        nombre[0] += 1
                    with LockCache:
                        Cache['type:1'][user_id] = {
                            "id": ids,
                            "updateTime": datetime.now(timezone.utc).date()
                        }
                    return ids
            elif data.status_code == 429:
                log("\033[0;93mRate limit exceeded, sleeping X seconds...\033[0m")
                time.sleep(random.uniform(0.5, 2))
                continue
        except Exception as e:
            print(f"Error RequestsWapper: {e}")
            print(traceback.format_exc())
            time.sleep(2)
            continue
    else:
        return None

def search(IDuserFInd: str, IDuser: str, Queue: queue.Queue, found_event: threading.Event, lockSET: threading.Lock, Set: set):
    while not found_event.is_set():
        try:
            userQueue = Queue.get(timeout=1)
        except Exception:
            continue

        with lockSET:
            if userQueue["id"] in Set:
                continue
            Set.add(userQueue["id"])


def worker(IDuserFInd: str, Queue: queue.Queue,
            Set: set, lock: threading.Lock, found_event: threading.Event,
            result: dict, proxy, nombre: int, Cache: pickle, LockCache: threading.Lock, log, lockNombre, compressor=None, QueueEnable=None) -> dict:
    
    while not found_event.is_set(): # while True:
        try:
            userQueue = Queue.get(timeout=1)
        except Exception:
            continue

        userQueue = compressor.unzip(userQueue)

        with lock:
            if userQueue["id"] in Set:
                #Queue.task_done()
                continue
            Set.add(userQueue["id"])
        try:
            #print(f"https://friends.roblox.com/v1/users/{userQueue['id']}/friends")
            #data = rq.get(f"https://friends.roblox.com/v1/users/{userQueue['id']}/friends")
            data = RequestsWapper(proxy, f"https://friends.roblox.com/v1/users/{userQueue['id']}/friends", method="GET",
                                  type=0, found_event=found_event, Cache=Cache, LockCache=LockCache, log=log, lockNombre=lockNombre, nombre=nombre, user_id=userQueue['id'], lock=lock)
            if data is None:
                return True
    
            for user in data:
                user = int(user)
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
                    if not QueueEnable.is_set():
                        try:
                            Queue.put(compressor.zip({"IDuserFInd": IDuserFInd, "id": user, "intermediate": userQueue["intermediate"] + [user]}), block=False)
                        except queue.Full:
                            QueueEnable.set()
                            #continue
                  #iun = unit(rq, uernameFind, user["id"], Queue=Queue, Set=Set)
                  #if iun["status"]:
                  #    iun["intermediate"].append(user["name"])
                  #    return iun
                      #return {"status": True, "username": user["username"], "id": user["id"]}
        except Exception as e:
          print(f"Error: {e}")
          print(traceback.format_exc())
    return True

def Gestion(lockQueue: threading.Lock, Queue: queue.Queue, found_event: threading.Event, windows_size: int = 1_000_000, QueueEnable: threading.Event = None, Cache: dict = None, LockCache: threading.Lock = None):
    if True == False:
        while not found_event.is_set():
            time.sleep(5)
            if Queue.qsize() > 20_000:
                for _ in range(Queue.qsize() - 20_000):
                    try:
                        Queue.get_nowait()
                    except queue.Empty:
                        pass
    if True == False:
        while not found_event.is_set():
            with lockQueue:
                size = Queue.qsize()
            if size > windows_size:
                QueueEnable.set()
                break
            else:
                time.sleep(2)
    if True == True:
        start_time = time.monotonic()
        while not found_event.is_set():
            if time.monotonic() - start_time >= 300: # 5 minutes
                with LockCache:
                    with open(f"CacheV2_{datetime.now(timezone.utc).strftime('%Y-%m-%d_%H-%M-%S')}.pkl", "wb") as f:
                        pickle.dump(Cache, f)
                start_time = time.monotonic()
            else:
                time.sleep(1)
        


def main():
    parser = argparse.ArgumentParser(description="Mon programme InterLinkerRoblox")
    parser.add_argument("--findin", type=str, default=None, help="Username")
    parser.add_argument("--findend", type=str, default=None, help="Username Find")
    parser.add_argument("--threads", type=int, default=1, help="Number of threads CPU to use")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode with detailed logging")
    parser.add_argument("--compress-queue", action="store_true", help="Enable compression of the queue")
    parser.add_argument("--window-size", type=int, default=1_000_000, help="Taille de la fenêtre pour l'analyse des utilisateurs")
    parser.add_argument(
        "--updateTimeCache",
        type=int,
        default=0,
        help="Nombre de jours d'un bloc de cache avant sa mise à jour"
    )
    #parser.add_argument("--cache", type=str, help="Chemin du fichier cache")
    
    args = parser.parse_args()
    for k, v in vars(args).items():
        sys.stdout.write(f"--{k} {v}, ")
    sys.stdout.write("\n")


    def log(msg: str):
        if args.debug:
            sys.stdout.write(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC] {msg}\n")
    
    class compressor:
        def __init__(self, enable: bool = True):
            self.enable = enable
            #self.ZstdCompressor = zstd.ZstdCompressor(level=22)
            #self.ZstdDecompressor = zstd.ZstdDecompressor()
        
        def zip(self, data: dict) -> bytes:
            ZstdCompressor = zstd.ZstdCompressor(level=22)
            if self.enable:
                return ZstdCompressor.compress(orjson.dumps(data))
            else:
                return data
        
        def unzip(self, data: bytes) -> dict:
            ZstdDecompressor = zstd.ZstdDecompressor()
            if self.enable:
                return orjson.loads(ZstdDecompressor.decompress(data))
            else:
                return data
    
    if args.compress_queue:
        Scompressor = compressor(enable=True)
    else:
        Scompressor = compressor(enable=False)

    if os.path.exists("CacheV2.pkl"):
        Cache = pickle.load(open("CacheV2.pkl", "rb"))
    else:
        Cache = {"type:1": {}, "TotalTime": 0.0}
    LockCache = threading.Lock()
    lock = threading.Lock()
    lockNombre = threading.Lock()
    rq = requests.Session()
    Queue = queue.Queue(maxsize=args.window_size) # 2_000_000
    found_event = threading.Event()
    QueueEnable = threading.Event()
    result = {"status": False}
    Set = set()
    nombre = [0]
    ThreadPool = ThreadPoolExecutor(max_workers=2_000_000)
    start_time = None

    try:
        if not args.findin:
            uername = input("Username>> ")
        else:
            uername = args.findin
        
        if not args.findend:
            uernameFind = input("Username Find>> ")
        else:
            uernameFind = args.findend
    
        data = rq.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [uername], "excludeBannedUsers": False})
        data.raise_for_status()
        IDuser = data.json()["data"][0]["id"]
        IDuser = int(IDuser)
        print(f"IDuser ID: {IDuser}" + "\n")
    
        data = rq.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [uernameFind], "excludeBannedUsers": False})
        data.raise_for_status()
        IDuserFInd = data.json()["data"][0]["id"]
        IDuserFInd = int(IDuserFInd)
        print(f"IDuserFInd ID: {IDuserFInd}" + "\n")
    
        Queue.put(Scompressor.zip({"IDuserFInd": IDuserFInd, "id": IDuser, "intermediate": [IDuser]}))
        
        if os.path.exists("config.json"):
            liste = []
            for _ in json.loads(open("config.json").read())["proxy"]:
                rq = requests.Session()
                rq.proxies.update({
                    "http": _,
                    "https": _
                })
                liste.append({"rq": rq, "lock": threading.Lock()})
            proxy = itertools.cycle(liste)
        else:
            raise Exception("config.json not found")

        ThreadPool.submit(Gestion, lock, Queue, found_event, windows_size=args.window_size, QueueEnable=QueueEnable, Cache=Cache, LockCache=LockCache)

        for _ in range(args.threads):
            ThreadPool.submit(worker, IDuserFInd, Queue, Set, lock, found_event, result, proxy, nombre, Cache, LockCache, log, lockNombre=lockNombre, compressor=Scompressor, QueueEnable=QueueEnable)
        print("Searching...")
        
        start_time = time.monotonic()
        with yaspin(spinner=Spinner(Spinners.material.frames, 100 * 5), text="Process en cours...", color="red", timer=True) as e:
            while not found_event.is_set():

                with lock:
                    users_scanned = len(Set)
                #with LockCache:
                #    CacheSize = asizeof.asizeof(Cache)
                with lockNombre:
                    NOMBRE = nombre[0]
                
                elapsed = time.monotonic() - start_time
                rpm = users_scanned / (elapsed / 60) if elapsed > 0 else 0
                e.text = (
                    f"Users scanned: {users_scanned} | "
                    f"Queue size: {Queue.qsize()} | "
                    f"Threads: {threading.active_count()} | "
                    f"nombre: {NOMBRE} | "
                    # f"Cache size: {CacheSize/(1024*1024):.2f} MB | "
                    f"Rate: {rpm:.2f} users/min"
                )
                time.sleep(2)
        print("\nFinished.")
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        found_event.set()

    ThreadPool.shutdown(wait=True)
    print(result)
    with open("CacheV2.pkl", "wb") as f:
        if start_time:
            Cache['TotalTime'] += (time.monotonic() - start_time)
            print(f"Time session: {(time.monotonic() - start_time):.4f} seconds")
        print(f"Total time life Cache: {Cache['TotalTime']:.4f} seconds")
        pickle.dump(Cache, f)


    #if data['status']:
    #    print("->".join(data["intermediate"][::-1]))
    #    #print(f"Found: {user['username']} | ID: {user['id']}")

if __name__ == "__main__":
    main()