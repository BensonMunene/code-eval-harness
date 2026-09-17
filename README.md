# Model Evaluator

An execution and grading harness for untrusted candidate code — built to study the
harder problem sitting underneath it: **how do you know your evaluation is any good?**

---

## The problem

Automated evaluation looks like a solved problem. Run the candidate against a test
suite, count the passes, report a score:

```
Candidate A ──> [ test suite ] ──> 9/10
```

The number is the easy part. The difficult question is what it entitles you to believe.
A score is never a measurement of the candidate alone — it is a joint measurement of the
candidate *and the instrument*. When the instrument is weak, the score is mostly about
the instrument.

So there are three systems under evaluation, not one:

```
                  task specification
                          │
                  ┌───────┴───────┐
                  ▼               ▼
         ┌─────────────┐   ┌─────────────┐
         │  candidate  │   │ test suite  │
         └──────┬──────┘   └──────┬──────┘
                └────────┬────────┘
                         ▼
                   ┌───────────┐
                   │ evaluator │──> judgment
                   └───────────┘
```

Most evaluation failures are not sandbox bugs. They are specification failures — the task
was loose enough that the candidate's answer was defensible, and the verifier called it
wrong anyway.

## The result that motivates this project

The repository evaluates implementations of an LRU cache. Below is a real run of the four
tests a competent developer writes by instinct, against two candidates: a correct LRU, and
a FIFO cache masquerading as one.

```
SUITE A — the tests you'd write without thinking about it
----------------------------------------------------------
test                                   correct        fifo
N1  basic put/get                         PASS        PASS
N2  overwrite a value                     PASS        PASS
N3  two keys, both under capacity         PASS        PASS
B1  inserting past capacity evicts        PASS        PASS
----------------------------------------------------------
score                                      4/4         4/4
```

Everything green, and the suite cannot distinguish an LRU cache from a FIFO cache — which
is the only property the task is about. Its **discriminating power is zero**: every
candidate receives an identical score, so the instrument outputs a constant.

One further test, derived rather than brainstormed, changes that:

```
SUITE B — same, plus one test derived from a named bug
----------------------------------------------------------
R1  a read counts as a use                PASS        FAIL
----------------------------------------------------------
score                                      5/5         4/5
```

`R1` was constructed by naming a specific wrong implementation (FIFO), identifying where
its behaviour diverges from the specification, and building the shortest input that reaches
that divergence. The process is mechanical, not creative.

## Design principles

These are the rules the project holds itself to. Each was derived from a concrete failure,
not adopted on principle.

**A task is well-formed only if you can state its oracle before you write it.**
Verifiability is an authoring-time constraint, not a downstream concern. Writing the
specification in this repository surfaced that the textbook LRU formulation — `get` returns
`-1` on a miss — is *unverifiable*: the miss signal lives inside the value domain, so
storing `-1` is indistinguishable from a cache miss. The task had to change, not the grader.

**Every test names the wrong implementation it kills.**
A test that cannot name one is decoration. This converts test design from taste into
derivation: enumerate the ways a competent engineer gets the problem subtly wrong, then
write one test per way.

**A test that every candidate passes carries no information.**
This is measurement, not quality assurance. The unit of value is discriminating power.

**Oracles are ranked by their resistance to gaming.**

| Oracle | Mechanism | Weakness |
|---|---|---|
| Hardcoded expectation | `assert f(5) == 120` | a finite lookup table; memorizable |
| Differential | compare against a reference implementation | requires a trusted reference |
| Property / invariant | assert what must be true of any answer | requires the property to be stated |
| Metamorphic | assert relations between related inputs | indirect evidence |

**Coverage is measured against specification clauses, not code lines.**
Line coverage measures the candidate. Clause coverage measures us.

**A score is not a sum.** A wrong answer, a crash, a hang, a correct answer computed in
O(n²), and a correct answer that leaks memory are distinct signals. Some are graded; some
are gates.

## What gets measured

| Dimension | Question | Failure mode it catches |
|---|---|---|
| Correctness | does it produce the expected result? | wrong logic |
| Robustness | does it hold up off the happy path? | missing validation, crashes |
| Performance | what is the complexity class? | correct but quadratic |
| Resources | memory, CPU, termination | correct, fast, and unbounded memory |

The dimensions are not independent. A candidate that does not terminate has no meaningful
performance score. Correctness gates everything downstream of it.

One implementation in the catalogue tracks recency by appending every access to a list and
lazily skipping stale entries. It is functionally correct and amortized O(1) — it passes
every correctness test and every timing test — and fails only on memory. That single case
is the argument for measuring resources at all.

## Repository layout

```
docs/
  01-task-spec-lru-cache.md   public specification — the exact text a candidate sees
  02-test-plan-lru-cache.md   private test plan — catalogue of wrong implementations
reference/
  naive.py                    the oracle: O(n), slow, auditable by eye
candidates/
  correct.py                  a genuinely correct O(1) implementation
  fifo.py                     evicts by insertion order — the common wrong answer
runner/
  step0.py                    discrimination demonstration
```

The separation between the public specification and the private test plan is structural,
not organisational. A candidate that can read the test plan can satisfy it without
implementing the specification.

## Quick start

Requires Python 3.12+. No dependencies.

```bash
git clone <repository-url> && cd model-evaluator
python3 runner/step0.py
```

## Roadmap

| Phase | Scope | Status |
|---|---|---|
| 1 | Define the evaluation problem — candidate, oracle, success, failure | Complete |
| 2 | Design the test suite — normal, boundary, invalid, adversarial, performance, resource | Specification and plan complete; implementation in progress |
| 3 | Execution sandbox — process isolation, timeouts, crash containment, resource measurement | Planned |
| 4 | Grader — dimensional scoring, fatal gates, no naive averaging | Planned |
| 5 | Attack the evaluator — hardcoded answers, visible-test overfitting, pathological inputs | Planned |
| 6 | Meta-evaluation — mutation testing to measure the suite's own discriminating power | Planned |

No sandbox exists yet, and that is deliberate: every candidate in the repository was written
here and is therefore trusted. Isolation becomes necessary when candidates arrive from
elsewhere, and not before.

## Why this design generalises

The structure is deliberately the one used to evaluate autonomous agents:

| This repository | Agent evaluation |
|---|---|
| task specification | task prompt |
| candidate behind a process boundary | agent under test |
| sandbox | environment |
| reference implementation | reference solution |
| test suite | verifier |
| mutation score | *does the verifier discriminate?* |

The candidate is held behind a process boundary even where a direct function call would be
simpler, because a process boundary is the only interface that extends to a candidate whose
output is a trajectory of actions rather than a return value.
