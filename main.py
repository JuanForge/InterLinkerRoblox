import sys
import time
import queue
import random
import requests
import threading

from concurrent.futures import ThreadPoolExecutor

def unit(rq: requests.Session, uernameFind: str, IDuser: str, Queue: queue.Queue, Set: set) -> dict:
    if not IDuser in Set:
        Set.add(IDuser)
        try:
          data = rq.get(f"https://friends.roblox.com/v1/users/{IDuser}/friends")
          time.sleep(random.uniform(0.5, 1.5))
    
          for user in data.json()["data"]:
              sys.stdout.write(user["name"].lower() + "\n")
        
              if user["name"].lower() == uernameFind.lower():
                  return {"status": True, "username": user["name"], "id": user["id"], "intermediate": [user["name"]]}
              else:
                  iun = unit(rq, uernameFind, user["id"], Queue=Queue, Set=Set)
                  if iun["status"]:
                      iun["intermediate"].append(user["name"])
                      return iun
                      #return {"status": True, "username": user["username"], "id": user["id"]}
        except Exception as e:
          print(f"Error: {e}")
    return {"status": False}



def main():
    uername = input("Username>> ")
    uernameFind = input("Username Find>> ")
    ThreadPool = ThreadPoolExecutor(max_workers=2)
    lock = threading.Lock()
    rq = requests.Session()
    Queue = queue.Queue(maxsize=200)
    Set = set()
    data = rq.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [uername], "excludeBannedUsers": False})
    IDuser = data.json()["data"][0]["id"]
    print(f"User ID: {IDuser}")

    data = unit(rq, uernameFind, IDuser, Queue=Queue, Set=Set, lock=lock)

    if data['status']:
        print("->".join(data["intermediate"][::-1]))
        #print(f"Found: {user['username']} | ID: {user['id']}")

if __name__ == "__main__":
    main()