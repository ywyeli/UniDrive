from queue import Queue
from queue import Empty

class callbackHandler(object):
    def __init__(self):
        self.queue = Queue(100)

    def __call__(self, obj, name, queue):
        self.put(obj, name, queue)

    def put(self, obj, name, queue):
        queue.put((obj, name))

    def get(self):
        return self.queue.get(True, 1.0)
