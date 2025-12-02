import numpy as np
import matplotlib.pyplot as plt

print(">>> sandpile_2d_micro_fit.py starting up...")

# ---------- PARAMETERS (2D MICRO + FIT) ----------
N = 16               # grid size: N x N
THRESHOLD = 4        # topple when height >= 4
BURN_IN_STEPS = 1_000
MEASURE_STEPS = 5_000
RANDOM_SEED = 123
# -------------------------------------------------

rng = np.random.default_rng(RANDOM_SEED)

# 2D grid of "heights"
grid = np.zeros((N, N), dtype=np.int32)


def neighbors_2d(i, j, N):
    """Von Neumann neighbors (up, down, left, right) with open boundaries."""
    if i > 0:
        yield i - 1, j
    if i < N - 1:
        yield i + 1, j
    if j > 0:
        yield i, j - 1
    if j < N - 1:
        yield i, j + 1


def drop_grain():
    i = rng.integers(0, N)
    j = rng.integers(0, N)
    grid[i, j] += 1


def relax_once(record_avalanche: bool = False):
    avalanche_size = 0
    topple_mask = grid >= THRESHOLD

    while np.any(topple_mask):
        is_, js_ = np.where(topple_mask)
        num_topples = len(is_)
        avalanche_size += num_topples

        grid[is_, js_] -= THRESHOLD

        for i, j in zip(is_, js_):
            for ni, nj in neighbors_2d(i, j, N):
                grid[ni, nj] += 1

        topple_mask = grid >= THRESHOLD

    if record_avalanche and avalanche_size > 0:
        return avalanche_size
    else:
        return None


def run_simulation():
    print("Burn-in phase (2D micro sandpile)...", flush=True)
    for _ in range(BURN_IN_STEPS):
        drop_grain()
        relax_once(record_avalanche=False)

    print("Measurement phase (2D micro sandpile)...", flush=True)
    avalanche_sizes = []
    for _ in range(MEASURE_STEPS):
        drop_grain()
        size = relax_once(record_avalanche=True)
        if size is not None:
            avalanche_sizes.append(size)

    return np.array(avalanche_sizes, dtype=np.int64)


def fit_power_law(centers, hist):
    # keep only positive densities
    mask = hist > 0
    centers = centers[mask]
    hist = hist[mask]

    if len(centers) < 3:
        return None, None, 0

    log_x = np.log10(centers)
    log_y = np.log10(hist)

    # middle range: drop lowest & highest quartiles
    q1, q3 = np.quantile(log_x, [0.25, 0.75])
    mid_mask = (log_x >= q1) & (log_x <= q3)

    log_x_mid = log_x[mid_mask]
    log_y_mid = log_y[mid_mask]

    if len(log_x_mid) < 3:
        return None, None, 0

    # linear fit
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
        print(f"Fitted power-law exponent (2D): {exponent:.3f}")
        print(f"R^2 over middle range: {r2:.3f} (n={npts} points)")
    else:
        print("Not enough points for a reliable fit.")

    plt.figure()
    plt.loglog(centers, hist, marker='o', linestyle='none', label="data")
    plt.xlabel("Avalanche size (log scale)")
    plt.ylabel("Probability density (log scale)")
    plt.title(f"2D Micro Sandpile Avalanches (N={N}, steps={MEASURE_STEPS})")
    plt.grid(True, which='both', linestyle='--', alpha=0.3)
    plt.legend()
    plt.show()


def main():
    print(">>> Entering main()", flush=True)
    avalanches = run_simulation()
    print(f"Total avalanches recorded: {len(avalanches)}")
    plot_log_log_with_fit(avalanches)


if __name__ == "__main__":
    print(">>> __main__ guard triggered", flush=True)
    main()
