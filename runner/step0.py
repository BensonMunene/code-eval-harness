"""Step 0: no sandbox, no scoring. One question only —
does our test suite tell a correct implementation from a wrong one?"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(relpath, clsname="LRUCache"):
    path = ROOT / relpath
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, clsname)


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
CANDIDATES = {"correct": "candidates/correct.py", "fifo": "candidates/fifo.py"}


def run(suite, title):
    classes = {name: load(p) for name, p in CANDIDATES.items()}
    print(f"\n{title}")
    print("-" * 58)
    print(f"{'test':<34}" + "".join(f"{n:>12}" for n in classes))
    results = {n: 0 for n in classes}
    for t in suite:
        label = f"{t.__name__[2:]}  {t.__doc__}"
        row = f"{label[:34]:<34}"
        for name, C in classes.items():
            try:
                t(C)
                row += f"{'PASS':>12}"
                results[name] += 1
            except Exception:
                row += f"{'FAIL':>12}"
        print(row)
    print("-" * 58)
    print(f"{'score':<34}" + "".join(f"{str(results[n]) + '/' + str(len(suite)):>12}" for n in classes))
    return results


run(OBVIOUS, "SUITE A — the tests you'd write without thinking about it")
run(OBVIOUS + [t_R1], "SUITE B — same, plus one test derived from a named bug")
