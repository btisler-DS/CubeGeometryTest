````markdown
# CubeGeometryTest

This repository contains the small cube simulations used in the article
on the geometry of inquiry and self-organized criticality.

The goal is not to build a production library, but to preserve a
transparent record of what was actually run: simple sandpile models
that either self-organize, collapse, or run away under different
“inquiry-like” biases.

## Environments and dependencies

```bash
python 3.10+
pip install -r requirements.txt
````

## Inspirations

The initial cube and sandpile experiments were inspired by
the sandpile simulations demonstrated in Veritasium’s
videos and interactive examples:

- Sandpile Avalanche Simulation <https://www.veritasium.com/simulation3>
- 2D Ising Model: Criticality <https://www.veritasium.com/simulation4>
- Forest Fire Model (Drossel–Schwabl) <https://www.veritasium.com/simulation5>

The code in this repository is an independent implementation.

Main Python deps:

* numpy
* matplotlib
* scipy (for fitting, if used)

## Simulations

### Simulation 1 – Baseline (Neutral Symmetry)

* **Script:** `scripts/cube_sandpile_micro_fit.py`
* **Model:** 3D micro cube, no WWWWHW / WHY geometry
* **Behavior:** self-organized criticality with a clean power-law
  avalanche distribution.
* **Representative run:**

  * Max avalanche size ≈ 458
  * Fitted exponent: α ≈ 1.635
  * R² ≈ 0.996 over the middle range

Run:

```bash
python scripts/cube_sandpile_micro_fit.py
```

### Simulation 2 – External Forcing (GIGO)

* **Script:** `scripts/cube_WWWWHW_optionB_micro_fit.py`
* **Idea:** keep the internal physics neutral, but bias where grains
  land (overfeeding descriptive faces, starving causal ones).
* **Behavior:** criticality degrades; large avalanches are suppressed;
  in stronger forcing regimes the system may fail to reach a stable
  scaling law at all.

Run:

```bash
python scripts/cube_WWWWHW_optionB_micro_fit.py
```

### Simulation 3 – Internal Asymmetry (WHY Geometry)

Here the environment is neutral, but the *internal redistribution*
rules gently favor or penalize the WHY face while keeping total outflow
conserved.

#### 3A – WHY Attractor (enhanced cascades)

* **Script:** `scripts/cube_WWWWHW_optionA_flux_true_FIXED.py`
* **Behavior:** system remains critical, but the exponent flattens
  (large cascades become more probable).

Run:

```bash
python scripts/cube_WWWWHW_optionA_flux_true_FIXED.py
```

#### 3B – WHY Sink (suppressed cascades)

* **Script:** `scripts/cube_WWWWHW_optionA_flux_safe.py`
* **Behavior:** system remains critical, but the exponent steepens
  (large cascades become rarer).

Run:

```bash
python scripts/cube_WWWWHW_optionA_flux_safe.py
```

## Figures

The `figures/` directory contains example avalanche distributions for
each simulation, saved from matplotlib:

* `sim1_baseline_3d_cube.png`
* `sim2_external_forcing_failure.png`
* `sim3_why_attractor.png`
* `sim3_why_sink.png`

These correspond to the plots used in the article.

````

---

## 4. `requirements.txt`

Create a simple `requirements.txt`:

```text
numpy
matplotlib
scipy
````

(If any script imports something else—e.g. `tqdm`, `pandas`—add it here.)

---

## 5. Git setup commands (once the files are in place)

From the `CubeGeometryTest` folder:

```bash
git init
git add .
git commit -m "Initial commit: cube geometry simulations"
```

Then on GitHub:

1. Create a new empty repo named `CubeGeometryTest`.
2. Follow GitHub’s instructions, typically:

```bash
git remote add origin https://github.com/<your-username>/CubeGeometryTest.git
git branch -M main
git push -u origin main
```

---
