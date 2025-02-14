from collections import OrderedDict
 
class LRUCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()  # Key = frame number, Value = dummy (not used)
        self.capacity = capacity

    def get(self, key: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)

    def put(self, key: int) -> None:
        self.cache[key] = None  # Value doesn't matter; track frame number (key)
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def pop(self) -> int:
        key, _ = self.cache.popitem(last=False)
        return key  # Return the evicted FRAME NUMBER