# Test Plan: LRU Cache

**Status:** private. Never shown to a candidate. Separation is structural, not
hygienic: a candidate that can read this can satisfy it without implementing
the spec.

## Rule of construction

Every test names the specific plausible wrong implementation it kills. A test
that cannot name one is decoration and does not go in the suite.

## Catalogue of wrong implementations

These are the hypotheses. The suite exists to discriminate against them.

| id | name | what it does wrong |
|----|------|--------------------|
| W1 | `UnboundedDict` | plain dict, never evicts |
| W2 | `FIFOCache` | evicts oldest *inserted*; `get` does not reorder |
| W3 | `UpdateNoPromote` | `d[k] = v` on an existing key without promoting it |
| W4 | `PutAlwaysInserts` | treats a put on an existing key as a new insert, evicting |
| W5 | `OffByOneEvict` | evicts when `len >= capacity` *before* insert, holding `capacity - 1` |
| W6 | `AssumesNonEmpty` | seeds from `keys[0]` / pops from an empty structure |
| W7 | `SentinelMinusOne` | returns `-1` on miss instead of raising |
| W8 | `AppendOnlyHistory` | tracks recency by appending to a list and lazily skipping stale entries — **correct and fast, unbounded memory** |
| W9 | `ListScan` | `order.remove(k)` / `order.index(k)` — **correct, O(n) per op** |
| W10 | `InsertOnMiss` | `get` miss inserts a placeholder (`setdefault` / `defaultdict`) |
| W11 | `Memorizer` | hardcodes outputs for recognised operation sequences |

## Oracle types

- **H** hardcoded expectation — cheap, memorizable, weakest evidence
- **D** differential against the naive reference implementation
- **P** property / invariant checked over generated input
- **M** metamorphic relation
- **R** resource measurement

## The suite

### Normal

| # | test | oracle | kills |
|---|------|--------|-------|
| N1 | `put(a,1); get(a) == 1` | H | total logic failure |
| N2 | overwrite: `put(a,1); put(a,2); get(a) == 2` | H | write-once implementations |
| N3 | two keys under capacity, both retrievable | H | premature eviction |

### Boundary

| # | test | oracle | kills |
|---|------|--------|-------|
| B1 | capacity 2, insert 3rd key → first evicted | H | **W1** |
| B2 | capacity 1: `put(a); put(b)` → only `b` alive | H | **W5**, single-node linked-list bugs where MRU and LRU are the same node |
| B3 | capacity 0: `put(a)` is a no-op, `get(a)` raises, `len == 0` | H | **W6** |
| B4 | `capacity = -1` raises `ValueError` | H | missing validation |
| B5 | `len()` never exceeds capacity across a long random sequence | P | **W1**, **W5** |

### Recency semantics — the discriminating core

| # | test | oracle | kills |
|---|------|--------|-------|
| R1 | cap 2: `put(a); put(b); get(a); put(c)` → **`b`** evicted, `a` alive | H | **W2** — the single most common subtle bug. Every test above this line passes under FIFO. |
| R2 | cap 2: `put(a); put(b); put(a,9); put(c)` → `b` evicted, `a == 9` | H | **W3** |
| R3 | cap 2: `put(a); put(b); put(a,9)` → both alive, `len == 2` | H | **W4** |
| R4 | `get` on a missing key leaves the key set unchanged | P | **W10** |
| R5 | a missing `get` does not evict: cap 2, `put(a); put(b); get(zz)` → both alive | H | **W10** |
| R6 | re-put a previously evicted key; it behaves as a fresh insert | H | stale entries left in the recency structure after eviction |

### Invalid

| # | test | oracle | kills |
|---|------|--------|-------|
| I1 | `get` miss raises `KeyError`, not a sentinel return | H | **W7** |
| I2 | store `-1`, then `None`, then retrieve both | H | **W7** — a sentinel-based implementation cannot distinguish these from a miss |
| I3 | unhashable key propagates `TypeError` and does not mutate the cache | H | validation that swallows, or mutates before hashing |
| I4 | `LRUCache("2")` raises `TypeError` | H | missing type validation |

### Adversarial / differential

| # | test | oracle | kills |
|---|------|--------|-------|
| A1 | random op sequences (seeded) against the naive reference, compared step by step | D | **W11**, and every recency bug we failed to imagine |
| A2 | full invariant set over generated sequences: `len <= capacity`; live keys are exactly the `capacity` most-recently-used distinct keys | P | W2, W3, W5 again, without naming them |
| A3 | replaying the same op sequence on a fresh cache yields identical results | M | hidden global state shared between instances |
| A4 | two independent instances do not interfere | M | class-level rather than instance-level storage |

### Performance

| # | test | oracle | kills |
|---|------|--------|-------|
| P1 | 10^6 ops at capacity 10^3; wall time bounded | R | **W9** — invisible below ~10^4 ops |
| P2 | timing ratio across n, 2n, 4n stays roughly linear | M+R | **W9** without hardcoding a machine-dependent threshold |

### Resource

| # | test | oracle | kills |
|---|------|--------|-------|
| X1 | 10^6 distinct keys at capacity 10^2; peak RSS bounded by a function of capacity | R | **W8** — passes every correctness test and every timing test above |
| X2 | pathological input terminates within the timeout | R | non-termination in eviction loops |

## Note on P2

An absolute time limit encodes the grading machine. A ratio across input sizes
measures the complexity class itself and survives being run on different
hardware. Prefer the ratio; keep an absolute limit only as a crash guard.

## Coverage target

Coverage is measured against **spec clauses**, not code lines. Every normative
statement in `01-task-spec-lru-cache.md` must be exercised by at least one test.
Line coverage measures the candidate; clause coverage measures us.
