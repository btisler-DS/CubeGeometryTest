# CubeGeometryTest

This repository contains the code and figures for two related but distinct pieces of work:

1. **cube_geometry/** – Self-organized criticality (SOC) experiments on a cube with WWWWHW geometry.
2. **inquiry_studio/** – The cubic interrogative instrument used in the paper, which measures interrogative entropy and answer-side behavior for local LLM runs.

The Zenodo entry for the paper points to this repository as the canonical artifact.

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
