import requests
import queue


def main():
    uername = input("Username>> ")
    Queue = queue.Queue(maxsize=200)
