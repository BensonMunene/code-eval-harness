# Task Specification: LRU Cache

**Status:** public. This is the exact text a candidate sees. Nothing else.

Implement a class `LRUCache` in a module exposing that name.

## Constructor

`LRUCache(capacity: int)`

- `capacity` is the maximum number of key/value pairs held simultaneously.
- `capacity >= 0` is legal. A cache of capacity `0` holds nothing: every `put` is
  a no-op and every `get` raises `KeyError`.
- `capacity < 0` raises `ValueError`.
- `capacity` that is not an `int` (including `bool`, which is rejected) raises `TypeError`.

## Operations

`get(key) -> value`

- Returns the value associated with `key`.
- Raises `KeyError` if `key` is not present.
- On a **hit**, marks `key` as the most-recently-used entry.
- On a **miss**, changes nothing: no insertion, no eviction, no reordering.

`put(key, value) -> None`

- If `key` is already present: overwrites its value **and** marks it
  most-recently-used. No eviction occurs, regardless of how full the cache is.
- If `key` is absent and the cache holds fewer than `capacity` entries: inserts
  it as the most-recently-used entry.
- If `key` is absent and the cache holds exactly `capacity` entries: evicts
  exactly one entry — the least-recently-used — then inserts `key` as
  most-recently-used.

`__len__() -> int`

- Number of entries currently held. Must always satisfy `0 <= len(c) <= capacity`.

## Value and key domains

- Values may be **any** Python object, including `None` and `-1`. No value is
  reserved to signal absence; absence is signalled only by `KeyError`.
- Keys must be hashable. An unhashable key propagates the `TypeError` raised by
  hashing. It does not insert, evict, or otherwise mutate the cache.

## Recency ordering

Exactly two operations mark a key most-recently-used: a successful `get`, and
any `put` naming that key. Nothing else changes the ordering.

## Complexity

`get` and `put` must both run in **amortized O(1)** time, independent of
`capacity` and of the number of operations performed.

## Memory

Total memory held must be bounded by a function of `capacity` alone. It must not
grow with the number of distinct keys seen over the cache's lifetime.
