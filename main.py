import queue
import requests

from concurrent.futures import ThreadPoolExecutor



def main():
    uername = input("Username>> ")
    uernameFind = input("Username Find>> ")
    rq = requests.Session()
    #Queue = queue.Queue(maxsize=200)
    data = rq.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [uername], "excludeBannedUsers": False})
    IDuser = data.json()["data"][0]["id"]
    print(f"User ID: {IDuser}")

if __name__ == "__main__":
    main()