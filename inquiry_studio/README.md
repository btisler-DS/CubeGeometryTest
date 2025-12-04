```markdown
# CubeGeometryTest

This repository is the canonical code archive for the Zenodo-linked manuscript.

There are **two independent systems** inside this repository. They serve different purposes and should not be confused.

---

## 1. inquiry_studio/  (USED IN THE PAPER)

This directory contains the **actual measurement instrument** used to produce the results described in the manuscript.

If a reader wants to reproduce the claims in the paper, this is the code they should run.

### What it is

`inquiry_studio/` is a cubic interrogative engine. It measures how questions distribute across a structured WWWWHW lattice and logs answer-side behavior when run against a local language model.

It produces:

- interrogative entropy (H_I)
- answer-side entropy (H_A)
- deterministic question-field trajectories
- Type A / Type B / Type C session patterns referenced in the text

This is the system described in the paper as:

> “the cubic interrogative instrument”  
> “the cubic measurement system”  
> “the cubic backstop”

### Where to look

```

inquiry_studio/
src/
loop.py           ← ENTRY POINT
studio_config.py  ← experiment definitions
session.py        ← orchestration logic
metrics.py        ← entropy computations
inquiry_state.py  ← WWWWHW field state
cubic_dynamics.py ← update rules

```

### Minimal run instructions

From the repository root:

```

cd inquiry_studio
python -m pip install -r requirements.txt
python -m src.loop

```

This executes the configured experiments exactly as defined in `studio_config.py`.

Running with different prompts, adapters, or models is a **new experiment**, not a replication.

---

## 2. cube_geometry/  (SUPPORTING WORK)

This directory contains **geometric and physical intuition experiments** based on sandpile dynamics on a cube.

It is NOT the paper instrument.

It exists to show how applying bias to a cube produces:

- criticality
- breakdown of scaling laws
- exponent deformation
- attractor and sink behavior

This work informs the theory but is not the dataset used to generate paper results.

### Where to look

```

cube_geometry/
scripts/   ← sandpile and cube simulations
figures/   ← avalanche plots

```

Typical execution:

```

cd cube_geometry
python scripts/cube_sandpile_micro_fit.py

```

---

## Relationship

| Directory | Role | Used in paper |
|-----------|------|---------------|
| inquiry_studio | Measurement instrument | YES |
| cube_geometry | Supporting intuition | NO |
| README.md | Orientation | YES |

---

## Citation

https://github.com/btisler-DS/CubeGeometryTest

For instrumentation: cite `inquiry_studio/`  
For geometry experiments: cite `cube_geometry/`

---

End of clarification.
```
