"""Shared by every task: load candidates, run a suite, print the result table.

Candidates are still imported in-process, so a hostile candidate can stop this
runner. That is a known defect, documented in the README, and is Phase 3 work.
"""
import importlib.util
from pathlib import Path


def load(path, clsname):
    path = Path(path)
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, clsname)


def run(suite, title, candidates, clsname):
    classes = {name: load(p, clsname) for name, p in candidates.items()}
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
