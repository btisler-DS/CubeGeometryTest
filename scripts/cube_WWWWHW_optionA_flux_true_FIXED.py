import numpy as np
import matplotlib.pyplot as plt

print(">>> cube_WWWWHW_optionA_flux_true_FIXED.py starting up...")

# ---------- PARAMETERS (3D WWWWHW + WHY ATTRACTOR, CONSERVED) ----------
L = 12                # cube size
THRESHOLD = 6         # topple threshold
BURN_IN_STEPS = 5_000
MEASURE_STEPS = 10_000
RANDOM_SEED = 123

# Asymmetry: WHY face is a mild attractor
# CRITICAL: Weights must sum to THRESHOLD to preserve conservation
WHY_BIAS = 1.2        # raw bias toward WHY
NORMAL_BIAS = 1.0     # raw bias for other directions

# Renormalize to ensure conservation:
TOTAL_RAW = WHY_BIAS + 5 * NORMAL_BIAS  # = 6.2
WHY_INFLOW_WEIGHT = WHY_BIAS * (THRESHOLD / TOTAL_RAW)      # ≈ 1.161
NORMAL_WEIGHT = NORMAL_BIAS * (THRESHOLD / TOTAL_RAW)       # ≈ 0.968

print(f"Conservation check: WHY_INFLOW_WEIGHT = {WHY_INFLOW_WEIGHT:.4f}")
print(f"Conservation check: NORMAL_WEIGHT = {NORMAL_WEIGHT:.4f}")
print(f"Conservation check: Total outflow = {WHY_INFLOW_WEIGHT + 5*NORMAL_WEIGHT:.4f}")
print(f"Conservation check: Should equal THRESHOLD = {THRESHOLD}")
# -----------------------------------------------------------------------

rng = np.random.default_rng(RANDOM_SEED)

# Height grid
grid = np.zeros((L, L, L), dtype=np.float64)

# Face order: [WHAT, WHY, HOW, WHO, WHEN, WHERE]
FACE_NAMES = ["WHAT", "WHY", "HOW", "WHO", "WHEN", "WHERE"]
FACE_WHAT, FACE_WHY, FACE_HOW, FACE_WHO, FACE_WHEN, FACE_WHERE = range(6)
face_flux = np.zeros(6, dtype=np.float64)

# Safety monitoring
safety_triggered_count = 0


def drop_grain_3d():
    """Uniform grain drop anywhere in the cube."""
    x = rng.integers(0, L)
    y = rng.integers(0, L)
    z = rng.integers(0, L)
    grid[x, y, z] += 1.0


def relax_once_3d(record: bool = False):
    """
    Relaxation step for 3D WWWWHW cube with WHY as mild attractor.
    
    CONSERVATION: Weights are renormalized so that each topple removes
    exactly THRESHOLD units and distributes exactly THRESHOLD units to
    neighbors (or out of bounds). This preserves energy conservation.
    
    If record is True, returns avalanche size and accumulates boundary flux;
    otherwise returns None and does not track flux.
    """
    global face_flux, safety_triggered_count

    avalanche_size = 0
    topple_mask = grid >= THRESHOLD

    safety_count = 0
    SAFETY_LIMIT = L * L * L * 100  # generous but finite

    while np.any(topple_mask):
        xs, ys, zs = np.where(topple_mask)
        num_topples = len(xs)
        avalanche_size += num_topples

        # Subtract threshold from each unstable cell
        grid[xs, ys, zs] -= THRESHOLD

        # For each toppled cell, distribute sand to neighbors or out of bounds
        for cx, cy, cz in zip(xs, ys, zs):
            # directions: (dx, dy, dz, face_index)
            # x=0 is WHY, x=L-1 is WHAT
            directions = [
                (-1,  0,  0, FACE_WHY),    # toward x=0 (WHY)
                ( 1,  0,  0, FACE_WHAT),   # toward x=L-1 (WHAT)
                ( 0, -1,  0, FACE_WHO),    # toward y=0 (WHO)
                ( 0,  1,  0, FACE_HOW),    # toward y=L-1 (HOW)
                ( 0,  0, -1, FACE_WHERE),  # toward z=0 (WHERE)
                ( 0,  0,  1, FACE_WHEN),   # toward z=L-1 (WHEN)
            ]

            for dx, dy, dz, fidx in directions:
                nx = cx + dx
                ny = cy + dy
                nz = cz + dz

                # Determine weight for this transfer
                if fidx == FACE_WHY:
                    w = WHY_INFLOW_WEIGHT
                else:
                    w = NORMAL_WEIGHT

                if 0 <= nx < L and 0 <= ny < L and 0 <= nz < L:
                    # Internal transfer
                    grid[nx, ny, nz] += w
                else:
                    # Sand leaves the system through this face
                    if record:
                        face_flux[fidx] += w

        topple_mask = grid >= THRESHOLD

        safety_count += 1
        if safety_count > SAFETY_LIMIT:
            safety_triggered_count += 1
            print(f"WARNING: Safety limit reached in avalanche #{avalanche_size}. "
                  f"Total safety triggers so far: {safety_triggered_count}")
            break

    if record and avalanche_size > 0:
        return avalanche_size
    elif record:
        return 0
    else:
        return None


def run_simulation_3d():
    global face_flux, safety_triggered_count
    face_flux[:] = 0.0  # reset flux counters
    safety_triggered_count = 0  # reset safety counter

    print(f"Burn-in phase (steps={BURN_IN_STEPS})...", flush=True)
    for step in range(BURN_IN_STEPS):
        if (step + 1) % 1000 == 0:
            print(f"  Burn-in step {step + 1}/{BURN_IN_STEPS}", flush=True)
        drop_grain_3d()
        relax_once_3d(record=False)

    print(f"Measurement phase (steps={MEASURE_STEPS})...", flush=True)
    avalanche_sizes = []
    for step in range(MEASURE_STEPS):
        if (step + 1) % 2000 == 0:
            print(f"  Measure step {step + 1}/{MEASURE_STEPS}", flush=True)

        drop_grain_3d()
        size = relax_once_3d(record=True)
        if size is not None and size > 0:
            avalanche_sizes.append(size)

    return np.array(avalanche_sizes, dtype=np.int64)


def fit_power_law(centers, hist):
    """Fit a line in log-log space to the middle of the distribution."""
    mask = hist > 0
    centers = centers[mask]
    hist = hist[mask]

    if len(centers) < 3:
        return None, None, 0

    log_x = np.log10(centers)
    log_y = np.log10(hist)

    # Use interquartile range of log_x as "middle" regime
    q1, q3 = np.quantile(log_x, [0.25, 0.75])
    mid_mask = (log_x >= q1) & (log_x <= q3)

    log_x_mid = log_x[mid_mask]
    log_y_mid = log_y[mid_mask]

    if len(log_x_mid) < 3:
        return None, None, 0

    a, b = np.polyfit(log_x_mid, log_y_mid, 1)
    y_pred = a * log_x_mid + b
    ss_res = np.sum((log_y_mid - y_pred) ** 2)
    ss_tot = np.sum((log_y_mid - np.mean(log_y_mid)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else None

    exponent = -a
    return exponent, r2, len(log_x_mid)


def plot_log_log_with_fit(avalanche_sizes: np.ndarray):
    if avalanche_sizes.size == 0:
        print("No avalanches recorded; nothing to plot.")
        return

    avalanche_sizes = avalanche_sizes[avalanche_sizes > 0]
    min_size = avalanche_sizes.min()
    max_size = avalanche_sizes.max()

    print(f"Min avalanche size: {min_size}")
    print(f"Max avalanche size: {max_size}")
    print(f"Number of avalanches: {len(avalanche_sizes)}")

    if min_size == max_size:
        print("All avalanches the same size; no distribution to fit.")
        return

    num_bins = min(20, max(5, int(np.log10(max_size / max(min_size, 1))) * 5))
    if num_bins < 5:
        num_bins = 5

    bins = np.logspace(np.log10(min_size), np.log10(max_size), num_bins)
    hist, edges = np.histogram(avalanche_sizes, bins=bins, density=True)
    centers = np.sqrt(edges[:-1] * edges[1:])

    exponent, r2, npts = fit_power_law(centers, hist)

    if exponent is not None:
        print(f"Fitted power-law exponent (3D WHY-attractor, CONSERVED): {exponent:.3f}")
        print(f"R^2 over middle range: {r2:.3f} (n={npts} points)")
    else:
        print("Not enough points for a reliable fit.")

    plt.figure()
    plt.loglog(centers, hist, marker='o', linestyle='none', label="data")
    plt.xlabel("Avalanche size (log scale)")
    plt.ylabel("Probability density (log scale)")
    plt.title(f"3D WWWWHW Cube Avalanches (WHY attractor, conserved, L={L})")
    plt.grid(True, which='both', linestyle='--', alpha=0.3)
    plt.legend()
    plt.show()


def report_flux():
    """Print total and percentage flux per face."""
    total_flux = float(np.sum(face_flux))
    print("\n=== Boundary Flux by Face (measurement phase only) ===")
    print(f"Total flux (all faces): {total_flux:.3f}")
    if total_flux <= 0:
        print("No flux recorded.")
        return

    for name, val in zip(FACE_NAMES, face_flux):
        pct = 100.0 * val / total_flux
        print(f"{name:6s}: {val:10.3f}  ({pct:6.2f}%)")


def report_safety():
    """Report how many times the safety limit was triggered."""
    print(f"\n=== Safety Limit Report ===")
    if safety_triggered_count == 0:
        print("Safety limit was never triggered. (Good!)")
    else:
        print(f"WARNING: Safety limit was triggered {safety_triggered_count} times.")
        print("This suggests the model may have non-terminating avalanches.")


def main():
    print(">>> Entering main() [3D WWWWHW, WHY attractor, CONSERVED + flux]", flush=True)
    avalanches = run_simulation_3d()
    print(f"Total avalanches recorded: {len(avalanches)}")
    plot_log_log_with_fit(avalanches)
    report_flux()
    report_safety()


if __name__ == "__main__":
    print(">>> __main__ guard triggered [3D WWWWHW, WHY attractor, CONSERVED]", flush=True)
    main()