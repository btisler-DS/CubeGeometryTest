import numpy as np
import matplotlib.pyplot as plt

# ---------- PARAMETERS (MICRO TEST) ----------
N = 16               # grid size: N x N (small & fast)
THRESHOLD = 4        # classical sandpile: topple when height >= 4
BURN_IN_STEPS = 1_000
MEASURE_STEPS = 5_000
RANDOM_SEED = 123
# --------------------------------------------

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
    """Drop one grain at a random location."""
    i = rng.integers(0, N)
    j = rng.integers(0, N)
    grid[i, j] += 1


def relax_once(record_avalanche: bool = False):
    """
    Perform relaxation after a single grain drop.
    Returns avalanche size if record_avalanche is True, otherwise None.
    """
    avalanche_size = 0

    # Find initial unstable sites
    topple_mask = grid >= THRESHOLD

    # Process waves until no cell is unstable
    while np.any(topple_mask):
        # Indices of cells that will topple in this wave
        is_, js_ = np.where(topple_mask)
        num_topples = len(is_)
        avalanche_size += num_topples

        # Subtract from toppled cells
        grid[is_, js_] -= THRESHOLD

        # Distribute grains to neighbors
        for i, j in zip(is_, js_):
            for ni, nj in neighbors_2d(i, j, N):
                grid[ni, nj] += 1

        # Recompute unstable sites
        topple_mask = grid >= THRESHOLD

    if record_avalanche and avalanche_size > 0:
        return avalanche_size
    else:
        return None


def run_simulation():
    print("Burn-in phase (2D micro sandpile)...")
    for t in range(BURN_IN_STEPS):
        drop_grain()
        relax_once(record_avalanche=False)
        # no need for progress prints at this size

    print("Measurement phase (2D micro sandpile)...")
    avalanche_sizes = []
    for t in range(MEASURE_STEPS):
        drop_grain()
        size = relax_once(record_avalanche=True)
        if size is not None:
            avalanche_sizes.append(size)

    return np.array(avalanche_sizes, dtype=np.int64)


def plot_log_log(avalanche_sizes: np.ndarray):
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
        print(f"All avalanches have the same size ({min_size}); "
              f"distribution is degenerate.")
        return

    # Logarithmic bins
    num_bins = min(20, max(5, int(np.log10(max_size / max(min_size, 1))) * 5))
    if num_bins < 5:
        num_bins = 5

    bins = np.logspace(np.log10(min_size), np.log10(max_size), num_bins)

    hist, edges = np.histogram(avalanche_sizes, bins=bins, density=True)
    centers = np.sqrt(edges[:-1] * edges[1:])  # geometric mean of bin edges

    plt.figure()
    plt.loglog(centers, hist, marker='o', linestyle='none')
    plt.xlabel("Avalanche size (log scale)")
    plt.ylabel("Probability density (log scale)")
    plt.title(f"2D Micro Sandpile Avalanches (N={N}, steps={MEASURE_STEPS})")
    plt.grid(True, which='both', linestyle='--', alpha=0.3)
    plt.show()


def main():
    avalanche_sizes = run_simulation()
    print(f"Total avalanches recorded: {len(avalanche_sizes)}")
    plot_log_log(avalanche_sizes)


if __name__ == "__main__":
    main()
