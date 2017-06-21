import threading

def safely(func):
    try: return func()
    except: return None

def get_locker():
    lock = threading.Lock()
    def locker(func, lock=lock):
        lock.acquire()
        try: return func()
        finally: lock.release()
    return locker
