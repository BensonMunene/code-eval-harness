"""A genuinely correct O(1) implementation."""
from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity):
        if isinstance(capacity, bool) or not isinstance(capacity, int):
            raise TypeError("capacity must be an int")
        if capacity < 0:
            raise ValueError("capacity must be >= 0")
        self.capacity = capacity
        self.d = OrderedDict()

    def get(self, key):
        hash(key)
        if key not in self.d:
            raise KeyError(key)
        self.d.move_to_end(key)
        return self.d[key]

    def put(self, key, value):
        hash(key)
        if self.capacity == 0:
            return
        if key in self.d:
            self.d.move_to_end(key)
        elif len(self.d) >= self.capacity:
            self.d.popitem(last=False)
        self.d[key] = value

    def __len__(self):
        return len(self.d)
