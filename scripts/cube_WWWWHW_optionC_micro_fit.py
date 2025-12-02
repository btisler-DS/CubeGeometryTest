import numpy as np
import matplotlib.pyplot as plt

print(">>> cube_WWWWHW_optionC_micro_fit.py starting up...")

# ---------- PARAMETERS (3D WWWWHW + DIRECTIONAL COUPLING) ----------
L = 12               # cube size: L x L x L
THRESHOLD = 6        # topple when height >= 6
BURN_IN_STEPS = 2_000
MEASURE_STEPS = 5_000
RANDOM_SEED = 123

# Directional weights along WHAT <-> WHY axis (x direction)
W_TOWARD_WHY = 1.3   # steps with nx < cx (toward x = 0 / WHY)
W_TOWARD_WHAT = 0.7  # steps with nx > cx (toward x = L-1 / WHAT)
NORMAL_WEIGHT = 1.0  # y/z directions
# -------------------------------------------------------------

rng = np.random.default_rng(RANDOM_SEED)

# 3D grid of "heights"
grid = np.zeros((L, L, L), dtype=np.float64)

# Face assignment (for interpretation only):
# +X: WHAT   (x = L-1)
# -X: WHY    (x = 0)
# +Y: HOW    (y = L-1)
# -Y: WHO    (y = 0)
# +Z: WHEN   (z = L-1)
# -Z: WHERE  (z = 0)


def neighbors_3d(x, y, z, L):
    """6-neighbor topology on a 3D cube with open boundaries."""
    if x > 0:
        yield x - 1, y, z
    if x < L - 1:
        yield x + 1, y, z
    if y > 0:
        yield x, y - 1, z
    if y < L - 1:
        yield x, y + 1, z
    if z > 0:
        yield x, y, z - 1
    if z < L - 1:
        yield x, y, z + 1


def drop_grain_uniform():
    """Uniform random grain drop over the entire cube."""
    x = rng.integers(0, L)
    y = rng.integers(0, L)
    z = rng.integers(0, L)
    grid[x, y, z] += 1.0


def coupling_weight(cx, nx):
    """
    Determine weight for transfer from cell at x=cx to neighbor at x=nx
    along the WHAT <-> WHY axis.
      - nx < cx : step toward WHY (x=0)  -> higher weight
      - nx > cx : step toward WHAT (x=L-1) -> lower weight
      - nx == cx: no x-change (y/z direction) -> normal weight
    """
    if nx < cx:
        return W_TOWARD_WHY
    elif nx > cx:
        return W_TOWARD_WHAT
    else:
        return NORMAL_WEIGHT


def relax_once_3d(record_avalanche: bool = False):
    """
    Perform relaxation after a single grain drop (3D WWWWHW cube with
    directional coupling along WHAT <-> WHY axis).
    Returns avalanche size (number of topples) if record_avalanche is True,
    otherwise None.
    """
    avalanche_size = 0
    topple_mask = grid >= THRESHOLD

    while np.any(topple_mask):
        xs, ys, zs = np.where(topple_mask)
        num_topples = len(xs)
        avalanche_size += num_topples

        # topple: subtract threshold from unstable cells
        grid[xs, ys, zs] -= THRESHOLD

        # distribute to neighbors with directional weights along x
        for cx, cy, cz in zip(xs, ys, zs):
            for nx, ny, nz in neighbors_3d(cx, cy, cz, L):
                w = coupling_weight(cx, nx)
                grid[nx, ny, nz] += w

        topple_mask = grid >= THRESHOLD

    if record_avalanche and avalanche_size > 0:
        return avalanche_size
    else:
        return None


def run_simulation_3d():
    print("Burn-in phase (3D WWWWHW cube, Option C directional coupling)...", flush=True)
    for _ in range(BURN_IN_STEPS):
        drop_grain_uniform()
        relax_once_3d(record_avalanche=False)

    print("Measurement phase (3D WWWWHW cube, Option C directional coupling)...", flush=True)
    avalanche_sizes = []
    for _ in range(MEASURE_STEPS):
        drop_grain_uniform()
        size = relax_once_3d(record_avalanche=True)
        if size is not None:
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
        print(f"Fitted power-law exponent (3D Option C): {exponent:.3f}")
        print(f"R^2 over middle range: {r2:.3f} (n={npts} points)")
    else:
        print("Not enough points for a reliable fit.")

    plt.figure()
    plt.loglog(centers, hist, marker='o', linestyle='none', label="data")
    plt.xlabel("Avalanche size (log scale)")
    plt.ylabel("Probability density (log scale)")
    plt.title(f"3D WWWWHW Cube Avalanches (Option C directional coupling, L={L}, steps={MEASURE_STEPS})")
    plt.grid(True, which='both', linestyle='--', alpha=0.3)
    plt.legend()
    plt.show()


def main():
    print(">>> Entering main() [3D WWWWHW, Option C directional coupling]", flush=True)
    avalanches = run_simulation_3d()
    print(f"Total avalanches recorded: {len(avalanches)}")
    plot_log_log_with_fit(avalanches)


if __name__ == "__main__":
    print(">>> __main__ guard triggered [3D WWWWHW, Option C]", flush=True)
    main()
