"""Step 0: no sandbox, no scoring. One question only —
does our test suite tell a correct implementation from a wrong one?"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))  # repo root, so `harness` is importable

from harness.runner import run


# --- the tests a developer writes by instinct -------------------------------

def t_N1(C):
    """basic put/get"""
    c = C(2)
    c.put("a", 1)
    assert c.get("a") == 1


def t_N2(C):
    """overwrite a value"""
    c = C(2)
    c.put("a", 1)
    c.put("a", 2)
    assert c.get("a") == 2


def t_N3(C):
    """two keys, both under capacity"""
    c = C(2)
    c.put("a", 1)
    c.put("b", 2)
    assert c.get("a") == 1
    assert c.get("b") == 2


def t_B1(C):
    """inserting past capacity evicts something"""
    c = C(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)
    try:
        c.get("a")
        raise AssertionError("'a' should have been evicted")
    except KeyError:
        pass
    assert c.get("b") == 2
    assert c.get("c") == 3


# --- the test that actually asks whether this is an LRU ---------------------

def t_R1(C):
    """a read counts as a use"""
    c = C(2)
    c.put("a", 1)
    c.put("b", 2)
    c.get("a")                 # 'a' is now the most recently used
    c.put("c", 3)              # so the eviction victim must be 'b'
    assert c.get("a") == 1, "'a' was used most recently but got evicted"
    try:
        c.get("b")
        raise AssertionError("'b' was least recently used and should be gone")
    except KeyError:
        pass


OBVIOUS = [t_N1, t_N2, t_N3, t_B1]
CANDIDATES = {
    "correct": HERE / "candidates" / "correct.py",
    "fifo": HERE / "candidates" / "fifo.py",
}

run(OBVIOUS, "SUITE A — the tests you'd write without thinking about it",
    CANDIDATES, "LRUCache")
run(OBVIOUS + [t_R1], "SUITE B — same, plus one test derived from a named bug",
    CANDIDATES, "LRUCache")
