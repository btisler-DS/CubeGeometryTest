import numpy as np
import matplotlib.pyplot as plt

# --------- PARAMETERS YOU CAN TWEAK ---------
L = 24              # cube size: L x L x L
THRESHOLD = 5       # topples when height >= 5
P_PEBBLE = 1.0      # drop a pebble every time step
BURN_IN_STEPS = 50_000
MEASURE_STEPS = 200_000
RANDOM_SEED = 42
# -------------------------------------------

rng = np.random.default_rng(RANDOM_SEED)

# 3D grid of "load" values (the sandpile heights)
grid = np.zeros((L, L, L), dtype=np.int32)


def neighbors(x, y, z, L):
    """Yield valid 6-neighbors in the cube with fixed boundaries."""
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


def step_once(record_avalanche: bool = False):
    """Perform one time step.
    Optionally return avalanche size if recording."""
    global grid

    avalanche_size = 0

    # 1. Drop a pebble every step (slow driving, but continuous)
    x = rng.integers(0, L)
    y = rng.integers(0, L)
    z = rng.integers(0, L)
    grid[x, y, z] += 1

    # 2. Relaxation (toppling)
    topple_mask = grid >= THRESHOLD

    while np.any(topple_mask):
        # indices of cells that will topple
        xs, ys, zs = np.where(topple_mask)
        num_topples = len(xs)
        avalanche_size += num_topples

        # subtract from toppled cells
        grid[xs, ys, zs] -= THRESHOLD

        # distribute to neighbors
        for cx, cy, cz in zip(xs, ys, zs):
            for nx, ny, nz in neighbors(cx, cy, cz, L):
                grid[nx, ny, nz] += 1

        # recompute topple mask
        topple_mask = grid >= THRESHOLD

    if record_avalanche and avalanche_size > 0:
        return avalanche_size
    else:
        return None


def run_simulation():
    print("Burn-in phase...")
    for i in range(BURN_IN_STEPS):
        step_once(record_avalanche=False)
        if (i + 1) % (BURN_IN_STEPS // 10) == 0:
            print(f"  Burn-in {i + 1}/{BURN_IN_STEPS}")

    print("Measurement phase...")
    avalanche_sizes = []
    for i in range(MEASURE_STEPS):
        size = step_once(record_avalanche=True)
        if size is not None:
            avalanche_sizes.append(size)
        if (i + 1) % (MEASURE_STEPS // 10) == 0:
            print(
                f"  Measure {i + 1}/{MEASURE_STEPS}, "
                f"avalanches recorded: {len(avalanche_sizes)}"
            )

    return np.array(avalanche_sizes, dtype=np.int64)


def plot_log_log(avalanche_sizes: np.ndarray):
    # Guard: if no avalanches, avoid crash
    if avalanche_sizes.size == 0:
        print("No avalanches recorded; nothing to plot.")
        return

    # Filter out size 0 (shouldn't be present, but just in case)
    avalanche_sizes = avalanche_sizes[avalanche_sizes > 0]

    min_size = avalanche_sizes.min()
    max_size = avalanche_sizes.max()
    if min_size == max_size:
        print(f"All avalanches have the same size ({min_size}); "
              f"distribution is degenerate.")
        return

    num_bins = 50
    bins = np.logspace(np.log10(min_size), np.log10(max_size), num_bins)

    hist, edges = np.histogram(avalanche_sizes, bins=bins, density=True)
    centers = np.sqrt(edges[:-1] * edges[1:])  # geometric mean for bin centers

    plt.figure()
    plt.loglog(centers, hist, marker='o', linestyle='none')
    plt.xlabel("Avalanche size (log scale)")
    plt.ylabel("Probability density (log scale)")
    plt.title(f"Cubic Sandpile Avalanches (L={L}, steps={MEASURE_STEPS})")
    plt.grid(True, which='both', linestyle='--', alpha=0.3)
    plt.show()


def main():
    avalanche_sizes = run_simulation()
    print(f"Total avalanches recorded: {len(avalanche_sizes)}")
    plot_log_log(avalanche_sizes)


if __name__ == "__main__":
    main()
