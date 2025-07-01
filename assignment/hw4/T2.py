import threading
from threading import Thread
import time

lock = threading.Lock()

l = []

def thread_func(id, instructions):
    global l
    has_lock = False
    for inst in instructions:
        time.sleep(0.1)
        _id, op = inst

        if _id != id:
            continue
        
        if op == 1:
            lock.acquire()
            has_lock = True
        elif op == -1:
            if has_lock:
                lock.release()
                has_lock = False
        elif op == 0:
            if has_lock:
                l.append(id)
                print(l)
    
    return

num_threads, num_instructions = map(int, input().split(' '))

instructions = []
for i in range(num_instructions):
    instructions.append([item for item in map(int, input().split(' '))])

threads = []
for id in range(num_threads):
    thread = Thread(target=thread_func, args=(id, instructions))
    threads.append(thread)
    thread.start() 
for thread in threads:
    thread.join()