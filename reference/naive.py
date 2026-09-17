"""The oracle. Deliberately slow and obviously correct — we must be able to
audit this by eye, because everything else is judged against it."""


class NaiveLRU:
    def __init__(self, capacity):
        if isinstance(capacity, bool) or not isinstance(capacity, int):
            raise TypeError("capacity must be an int")
        if capacity < 0:
            raise ValueError("capacity must be >= 0")
        self.capacity = capacity
        self.items = []  # [key, value] pairs; index 0 = least recently used

    def _find(self, key):
        for i, (k, _) in enumerate(self.items):
            if k == key:
                return i
        return -1

    def get(self, key):
        hash(key)                      # unhashable keys raise before any mutation
        i = self._find(key)
        if i == -1:
            raise KeyError(key)
        item = self.items.pop(i)
        self.items.append(item)        # promote to most-recently-used
        return item[1]

    def put(self, key, value):
        hash(key)
        if self.capacity == 0:
            return
        i = self._find(key)
        if i != -1:
            self.items.pop(i)          # existing key: remove, re-append as MRU
        elif len(self.items) >= self.capacity:
            self.items.pop(0)          # full: evict least-recently-used
        self.items.append([key, value])

    def __len__(self):
        return len(self.items)
