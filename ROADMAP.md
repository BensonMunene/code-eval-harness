# Roadmap

**Goal:** make a small open coding model measurably better at backend work, and prove it with
scoring the model can't cheat.

This document is the plan, step by step. Each step says what to do, what you'll have at the end,
and how you know it's done. Work top to bottom and tick the boxes as you go.

---

## The big picture

```mermaid
flowchart LR
    subgraph P1["Build the checker"]
        direction TB
        S1["<b>1 · Task set</b><br/>backend tasks<br/>with hidden tests"]
        S2["<b>2 · Starting point</b><br/>score the model<br/>before training"]
        S1 --> S2
    end
    subgraph P2["Train"]
        direction TB
        S3["<b>3 · SFT</b><br/>learn from<br/>good examples"]
        S4["<b>4 · Preference pairs</b><br/>better vs worse<br/>answers"]
        S5["<b>5 · DPO</b><br/>learn to prefer<br/>the better answer"]
        S6["<b>6 · RL</b><br/>learn from<br/>rewarded attempts"]
        S3 --> S4 --> S5 --> S6
    end
    subgraph P3["Prove it"]
        direction TB
        S7["<b>7 · Catch cheating</b><br/>find and fix<br/>gamed tests"]
        S8["<b>8 · Report</b><br/>before vs after,<br/>on unseen tasks"]
        S7 --> S8
    end
    P1 --> P2 --> P3

    classDef now fill:#b45309,stroke:#92400e,color:#ffffff
    classDef later fill:#4b5563,stroke:#374151,color:#ffffff
    class S1 now
    class S2,S3,S4,S5,S6,S7,S8 later
```

<sub>Orange: in progress. Grey: not started.</sub>

After every training step (3, 5 and 6) the model is scored again the same way, so each step's
effect can be measured on its own.

## The four skills, in plain words

These are the skills the roles we're targeting ask for, and where this project shows each one.

| Skill | In plain words | Where it happens |
|---|---|---|
| **Supervised fine-tuning (SFT)** | show the model good examples until it copies them | step 3 |
| **Preference optimization (DPO)** | show it "this answer is better than that one" until it prefers the better kind | steps 4–5 |
| **RLHF / RLAIF** | let it try, score each try, reward the good ones; scores come from people (HF) or another AI (AIF) | steps 4 and 6 |
| **Domain adaptation** | make a general model good at one area | the whole project: the area is backend work |

## One idea holds it all together: the checker

Every task has hidden tests. Those tests are the checker, and every step depends on them.

```mermaid
flowchart TD
    C["<b>The checker</b><br/>hidden tests for every task"]
    SFT["<b>SFT</b><br/>training examples must<br/>pass the tests"]
    DPO["<b>DPO</b><br/>passing answer = better<br/>failing answer = worse"]
    RL["<b>RL</b><br/>tests passed = reward"]
    SC["<b>Scoring</b><br/>pass rate on unseen tasks<br/>is the final result"]
    J["<b>AI judge</b><br/>for what tests can't check,<br/>such as readability"]
    Y["<b>You</b><br/>label a small sample<br/>to check the judge"]
    C --> SFT
    C --> DPO
    C --> RL
    C --> SC
    J --> DPO
    Y --> J

    classDef core fill:#0f766e,stroke:#115e59,color:#ffffff
    classDef human fill:#b45309,stroke:#92400e,color:#ffffff
    class C core
    class Y human
```

**If the checker is weak, every step learns the wrong thing.** That's the lesson from the LRU cache
example in this repo: four obvious tests gave a broken cache a perfect 4/4.

## Rule one: never score on what the model studied

```mermaid
flowchart LR
    ALL["<b>All tasks</b>"] --> TR["<b>Training tasks</b><br/><i>about 70%</i>"]
    ALL --> HO["<b>Held-out tasks</b><br/><i>about 30%</i>"]
    TR --> T["used by SFT, DPO and RL"]
    HO --> S["used only for scoring"]

    classDef train fill:#4b5563,stroke:#374151,color:#ffffff
    classDef held fill:#0f766e,stroke:#115e59,color:#ffffff
    class TR,T train
    class HO,S held
```

A model scored on tasks it trained on has memorised them. The score would be meaningless. Each
task is marked training or held-out when it's created, and that label never changes.

## Where everything runs

This laptop has no GPU, so the work is split:

```mermaid
flowchart LR
    L["<b>Your laptop</b><br/>write tasks and tests<br/>build the harness<br/>prepare the data"]
    G["<b>GitHub</b><br/>this repository"]
    K["<b>Free cloud GPU</b><br/>Kaggle or Google Colab<br/>generate answers<br/>train the model"]
    L -->|push| G
    G -->|clone| K
    K -->|scores and reports| G

    classDef box fill:#0f766e,stroke:#115e59,color:#ffffff
    class L,G,K box
```

Trained model files are large and stay out of Git. Only code, data, scores and reports are
committed.

This repository is private, so a Kaggle or Colab notebook can only clone it with a GitHub access
token. Keep the token in the notebook's secrets, never in a committed file.

---

## Step 1 · Build the task set `IN PROGRESS`

**Goal:** 30–50 small backend coding tasks, each with a spec, hidden tests and a reference answer.

**Why it comes first:** everything later learns from these tasks and is scored by them.

**You'll have:** one folder per task in `tasks/`, the same shape as `tasks/lru-cache/`.

### How one task gets made

```mermaid
flowchart LR
    subgraph Q["Write the question"]
        direction TB
        A["<b>Write the spec</b><br/><i>the prompt the model reads</i>"]
        B["<b>List the ways</b><br/>to get it wrong"]
        C["<b>Close each one</b><br/>with a sentence<br/>in the spec"]
        A --> B --> C
    end
    subgraph K["Write the checker"]
        direction TB
        D["<b>Reference answer</b><br/>correct on purpose"]
        E["<b>Wrong answers</b><br/>wrong on purpose"]
        F["<b>Hidden tests</b>"]
        D --> E --> F
    end
    subgraph V["Check the checker"]
        direction TB
        G{"Reference passes?<br/>Wrong answers fail?"}
        H["<b>Fix or add</b><br/>a test"]
        I["<b>Task done</b>"]
        G -->|no| H
        H --> G
        G -->|yes| I
    end
    Q --> K --> V

    classDef done fill:#0f766e,stroke:#115e59,color:#ffffff
    classDef fix fill:#b91c1c,stroke:#991b1b,color:#ffffff
    class I done
    class H fix
```

The spec is the prompt. If it's vague, a model that reads it differently isn't wrong. We are.

### Checklist

- [ ] Rate limiter, the first task (in progress, see below)
- [ ] More tasks, for example: pagination, retry with backoff, input validation, request
      deduplication, cursor encoding, config parsing
- [ ] Mark every task as training or held-out

### The first task: a rate limiter

The model will write a class that behaves like this:

```python
limiter = RateLimiter(limit=100, window_seconds=60, clock=...)

limiter.allow("user-42")   # True  -> let the request through
limiter.allow("user-42")   # False -> reject it (an API would return 429)
```

Each decision below closes one way the model could reasonably read the spec differently.

| # | Question | Decision |
|---|---|---|
| 1 | Fixed window or sliding window? | **Sliding window.** A client can't squeeze 200 requests into one second when the minute rolls over. |
| 2 | Exact count, or an approximation? | **Exact.** An approximation can let a few extra requests through, and then no test can say what "correct" is. |
| 3 | Is a request exactly `window_seconds` old still in the window? | **Open.** Recommended: no, it has expired. |
| 4 | How do tests control time? | Next |
| 5 | What about `limit` of 0, negative, or not a number? | Later |
| 6 | Is the limit counted separately for each key? | Later |
| 7 | Do rejected requests count toward the limit? | Later |
| 8 | Are old timestamps and idle keys cleaned up, so memory doesn't grow forever? | Later |

**The open question (3), drawn out.** With `limit=1` and `window_seconds=60`:

```mermaid
flowchart LR
    A["<b>t = 0</b><br/>allow('a') → True"]
    B{"<b>t = 60</b><br/>is the first request<br/>still in the window?"}
    C["<b>expired</b><br/>allow('a') → True"]
    D["<b>still counts</b><br/>allow('a') → False"]
    A --> B
    B -->|no| C
    B -->|yes| D

    classDef rec fill:#0f766e,stroke:#115e59,color:#ffffff
    classDef alt fill:#4b5563,stroke:#374151,color:#ffffff
    class C rec
    class D alt
```

Both answers are reasonable, so the spec has to pick one. A test at exactly t = 60 needs full
control of time, which is why the interface takes a `clock` (question 4).

---

## Step 2 · Measure the starting point

**Goal:** score the model before any training, so later scores have something to be compared with.

- [ ] Pick the model: start with a coding model of about 0.5B parameters, such as
      Qwen2.5-Coder-0.5B-Instruct
- [ ] Have it answer every held-out task several times
- [ ] Run every answer through the checker, **inside the sandbox**
- [ ] Record the pass rate

**Done when:** you have one pass rate you could defend.

**Why the sandbox is needed here:** from this step on, the code being tested was written by a
model, not by us. The README shows a candidate that stops the current runner with one line.
Running model code without isolation isn't safe.

## Step 3 · SFT: learn from good examples

**Goal:** teach the model by showing it correct answers.

- [ ] Turn each training task into an example: spec in, reference answer out
- [ ] Fine-tune with LoRA, which trains a small add-on instead of the whole model, on a cloud GPU
- [ ] Score on the held-out tasks

**Done when:** you can compare this score with step 2.

**Tools:** Hugging Face `transformers`, `trl` for training, `peft` for LoRA.

## Step 4 · Build preference pairs

**Goal:** a dataset of "better answer / worse answer" pairs.

```mermaid
flowchart LR
    T["<b>One training task</b>"]
    M["<b>The model writes</b><br/>several answers"]
    C["<b>The checker runs</b><br/>the hidden tests"]
    P["<b>Passing answer</b><br/>chosen"]
    F["<b>Failing answer</b><br/>rejected"]
    PAIR["<b>Preference pair</b>"]
    T --> M --> C
    C --> P --> PAIR
    C --> F --> PAIR

    classDef good fill:#0f766e,stroke:#115e59,color:#ffffff
    classDef bad fill:#b91c1c,stroke:#991b1b,color:#ffffff
    class P good
    class F bad
```

- [ ] Have the model answer each training task several times
- [ ] Pair a passing answer with a failing one
- [ ] When both answers pass, ask an AI judge which is clearer
- [ ] Label about 50 pairs yourself and measure how often the judge agrees with you

**Done when:** you have the pair dataset, and a number for how far the judge can be trusted.

## Step 5 · DPO: learn to prefer the better answer

**Goal:** train on the pairs from step 4.

- [ ] Train with DPO, starting from the step 3 model
- [ ] Score on the held-out tasks

**Done when:** you can compare this score with steps 2 and 3.

## Step 6 · RL: learn from rewarded attempts (optional)

**Goal:** let the model practise, with the tests deciding the reward.

- [ ] Reward = how many hidden tests an answer passes
- [ ] Train, for example with TRL's GRPO trainer
- [ ] Score on the held-out tasks

This is the heaviest step and needs the most GPU time, so it's optional. It's the same idea as
RLHF, with the tests giving the reward instead of people.

## Step 7 · Catch the cheating

**Goal:** make sure a higher score means better code, not better cheating.

```mermaid
flowchart TD
    A["<b>A new score comes in</b>"]
    B["<b>Read a sample</b><br/>of the passing answers"]
    C{"Genuinely correct, or<br/>gaming a weak test?"}
    D["<b>Keep the result</b>"]
    E["<b>Strengthen the tests</b>"]
    F["<b>Re-score every model</b><br/>with the stronger tests"]
    A --> B --> C
    C -->|correct| D
    C -->|gaming| E
    E --> F --> A

    classDef ok fill:#0f766e,stroke:#115e59,color:#ffffff
    classDef bad fill:#b91c1c,stroke:#991b1b,color:#ffffff
    class D ok
    class E bad
```

What cheating looks like:

- returning fixed answers that match the examples in the spec
- spotting a test's inputs and special-casing them
- catching every error so the code never crashes, while giving wrong answers

- [ ] Review passing answers from each trained model
- [ ] Record every trick found and the test that now catches it

**Done when:** no trick you find still passes.

## Step 8 · Report

**Goal:** one honest page showing what each step changed.

| Model | Held-out pass rate | Change |
|---|---|---|
| Starting model | | |
| + SFT | | |
| + DPO | | |
| + RL | | |

The report also states:

- [ ] that no held-out task appeared in any training data
- [ ] every cheating trick found, and how it was fixed
- [ ] how often the AI judge agreed with human labels

---

## Rules we keep

1. **Score only on held-out tasks.**
2. **A test is only useful if a real answer can fail it.**
3. **The spec is the prompt.** If it's vague, the mistake is ours, not the model's.
4. **Model-written code is untrusted.** It always runs in the sandbox.
5. **A higher score is a question, not a result.** Check it isn't cheating first.

## How we work

Every change goes on its own branch and into `main` through a pull request:

```mermaid
flowchart LR
    B["<b>New branch</b>"] --> C["<b>Commit</b>"] --> P["<b>Pull request</b><br/>explains why"] --> M["<b>Merge into main</b>"]

    classDef box fill:#0f766e,stroke:#115e59,color:#ffffff
    class B,C,P,M box
```
