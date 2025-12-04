markdown
# CubeGeometryTest

This repository contains the code and figures for two related but distinct pieces of work:

1. **cube_geometry/** – Self-organized criticality (SOC) experiments on a cube with WWWWHW geometry.
2. **inquiry_studio/** – The cubic interrogative instrument used in the paper, which measures interrogative entropy and answer-side behavior for local LLM runs.

The Zenodo entry for the paper points to this repository as the canonical artifact.

A literature reconnaissance report is included in `/docs/literature` for transparency.  
It documents search scope and context but does not function as validation or endorsement.
---

## Repository Layout

- `cube_geometry/`
  - `scripts/` – Sandpile and WWWWHW cube simulations:
    - `cube_sandpile.py`, `cube_sandpile_micro*.py`
    - `cube_WWWWHW_optionA_flux*.py`
    - `cube_WWWWHW_optionB_micro_fit.py`
    - `cube_WWWWHW_optionC_micro_fit.py`
    - `sandpile_2d*.py`
  - `figures/` – Example avalanche plots produced by the scripts.

- `inquiry_studio/`
  - `src/` – The interrogative measurement system:
    - `cubic_dynamics.py`, `inquiry_state.py`, `loop.py`, `session.py`, `metrics.py`, `studio_config.py`
    - `adapters/` – LLM adapter implementations (`llm_dummy.py`, `llm_local.py`)
    - `backstop/` – Safety / logging utilities and rules
  - `README.md` – How to run the Type A / Type B / Type C sessions.
  - `requirements.txt` – Minimal dependencies for the instrument.
  - `test_questions.txt` – Example question sets.

- `requirements.txt` (root) – Shared minimal scientific stack (e.g., `numpy`, `matplotlib`, `scipy`).
- `LICENSE.md` – License for this repository.
- `.gitignore` – Keeps virtual environments, logs, and compiled Python files out of version control.

---

## cube_geometry: Running the SOC Cube Experiments

From the repo root:

```bash
cd cube_geometry
python -m pip install -r ../requirements.txt
````

Example runs (from within `cube_geometry`):

```bash
# Baseline sandpile (no WWWWHW geometry)
python scripts/cube_sandpile_micro_fit.py

# WWWWHW option A – flux variants
python scripts/cube_WWWWHW_optionA_flux_true.py
python scripts/cube_WWWWHW_optionA_flux_safe.py

# WWWWHW option B / C – external forcing variants
python scripts/cube_WWWWHW_optionB_micro_fit.py
python scripts/cube_WWWWHW_optionC_micro_fit.py
```

Each script generates avalanche statistics and, in some cases, saves plots into `cube_geometry/figures/`.

---

## inquiry_studio: Interrogative Instrument Used in the Paper

The `inquiry_studio` directory contains the code for the cubic interrogative instrument used in the manuscript. It:

* Represents questions in a WWWWHW field (who/what/when/where/why/how).
* Computes interrogative entropy (H_I) over that field.
* Logs answer-side behavior (H_A and related metrics) for each step.
* Runs reproducible Type A / Type B / Type C sessions against a local LLM or dummy adapter.

Basic usage (from the repo root):

```bash
cd inquiry_studio
python -m pip install -r requirements.txt

# Example: run the configured sessions
python -m src.loop
```

The exact session definitions and question sets used in the paper are encoded in `src/studio_config.py` and the associated question files. To reproduce the manuscript, use this repository as-is and do not alter those definitions.

---

## Reproducibility Notes

* `cube_geometry/` provides SOC experiments for geometric and physical intuition (supporting work).
* `inquiry_studio/` is the **instrument actually used** to generate the interrogative entropy results in the paper.

Together, they form the computational backbone for the work described in the Zenodo-linked manuscript.

```
::contentReference[oaicite:0]{index=0}
```
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
