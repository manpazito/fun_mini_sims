import json
import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Cardinal unit directions used by the mathemagicland 2D walk.
CARDINAL_STEPS = np.array(
    [
        [1, 0],
        [0, 1],
        [-1, 0],
        [0, -1],
    ],
    dtype=int,
)


# =========================
# I/O helpers
# =========================


def ensure_output_dirs(base_output_dir):
    """Create output and paths directories and return both."""
    paths_dir = base_output_dir / "paths"
    base_output_dir.mkdir(parents=True, exist_ok=True)
    paths_dir.mkdir(parents=True, exist_ok=True)
    return base_output_dir, paths_dir


def save_json(payload, out_path):
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f)
    return out_path


def save_1d_path_json(path_positions, trial_index, paths_dir):
    payload = {
        "trial_index": int(trial_index),
        "positions": [int(v) for v in path_positions],
    }
    return save_json(payload, paths_dir / f"trial_{trial_index:04d}.json")


def save_2d_path_json(xs, ys, trial_index, paths_dir):
    payload = {
        "trial_index": int(trial_index),
        "x": [float(v) for v in xs],
        "y": [float(v) for v in ys],
    }
    return save_json(payload, paths_dir / f"trial_{trial_index:04d}.json")


def save_summary_csv(summary_df, out_path):
    summary_df.to_csv(out_path, index=False)
    return out_path


# =========================
# Single-walk simulators
# =========================


def simulate_unit_walk_1d(rng, max_steps):
    """1D ±1 walk, stop at first return to origin or max_steps."""
    position = 0
    positions = [position]

    min_position = 0
    max_position = 0
    max_abs_displacement = 0
    returned_to_origin = False

    for _ in range(max_steps):
        position += int(rng.choice((-1, 1)))
        positions.append(position)

        min_position = min(min_position, position)
        max_position = max(max_position, position)
        max_abs_displacement = max(max_abs_displacement, abs(position))

        if position == 0:
            # First return after leaving the origin.
            returned_to_origin = True
            break

    steps_until_stop = len(positions) - 1
    return_time = float(steps_until_stop) if returned_to_origin else np.nan

    return {
        "positions": positions,
        "steps_until_stop": steps_until_stop,
        "returned_to_origin": returned_to_origin,
        "censored": not returned_to_origin,
        "return_time": return_time,
        "max_abs_displacement": float(max_abs_displacement),
        "min_position": int(min_position),
        "max_position": int(max_position),
        "final_position": int(position),
    }


def simulate_cardinal_walk_2d(rng, max_steps):
    """2D cardinal walk, stop at first return to origin or max_steps."""
    x, y = 0, 0
    xs = [x]
    ys = [y]

    min_x = max_x = x
    min_y = max_y = y
    max_distance = 0.0
    max_manhattan = 0
    returned_to_origin = False

    for _ in range(max_steps):
        # Uniformly choose one of four cardinal directions.
        dx, dy = CARDINAL_STEPS[int(rng.integers(0, 4))]
        x += int(dx)
        y += int(dy)
        xs.append(x)
        ys.append(y)

        min_x = min(min_x, x)
        max_x = max(max_x, x)
        min_y = min(min_y, y)
        max_y = max(max_y, y)

        distance = math.hypot(x, y)
        max_distance = max(max_distance, distance)
        max_manhattan = max(max_manhattan, abs(x) + abs(y))

        if x == 0 and y == 0:
            # First return to origin.
            returned_to_origin = True
            break

    steps_until_stop = len(xs) - 1
    return_time = float(steps_until_stop) if returned_to_origin else np.nan
    bbox_width = max_x - min_x
    bbox_height = max_y - min_y

    return {
        "xs": xs,
        "ys": ys,
        "steps_until_stop": steps_until_stop,
        "returned_to_origin": returned_to_origin,
        "censored": not returned_to_origin,
        "return_time": return_time,
        "max_distance": float(max_distance),
        "max_manhattan": int(max_manhattan),
        "bbox_width": int(bbox_width),
        "bbox_height": int(bbox_height),
        "bbox_area": int(bbox_width * bbox_height),
        "final_x": int(x),
        "final_y": int(y),
    }


def get_direction_vectors(n_directions):
    if n_directions < 2:
        raise ValueError("N_DIRECTIONS must be >= 2")

    if n_directions == 2:
        return np.array([[1.0, 0.0], [-1.0, 0.0]], dtype=float)

    if n_directions == 4:
        # Keep N=4 exactly on the integer lattice.
        return CARDINAL_STEPS.astype(float)

    angles = 2.0 * np.pi * np.arange(n_directions) / n_directions
    return np.column_stack((np.cos(angles), np.sin(angles)))


def reached_origin(x, y, n_directions, tolerance):
    if n_directions in (2, 4):
        # Exact equality is stable for these lattice cases.
        return (x == 0.0) and (y == 0.0)
    # Tolerance check protects against floating-point accumulation.
    return math.hypot(x, y) <= tolerance


def simulate_general_walk(
    rng, n_directions, max_steps, return_tolerance, round_decimals
):
    vectors = get_direction_vectors(n_directions)

    x, y = 0.0, 0.0
    xs = [x]
    ys = [y]

    min_x = max_x = x
    min_y = max_y = y
    max_distance = 0.0
    max_manhattan = 0.0
    returned_to_origin = False

    for _ in range(max_steps):
        dx, dy = vectors[int(rng.integers(0, n_directions))]
        x += float(dx)
        y += float(dy)

        if n_directions not in (2, 4):
            # Rounding keeps tiny drift from growing over long walks.
            x = float(np.round(x, decimals=round_decimals))
            y = float(np.round(y, decimals=round_decimals))

        xs.append(x)
        ys.append(y)

        min_x = min(min_x, x)
        max_x = max(max_x, x)
        min_y = min(min_y, y)
        max_y = max(max_y, y)

        distance = math.hypot(x, y)
        max_distance = max(max_distance, distance)
        max_manhattan = max(max_manhattan, abs(x) + abs(y))

        if reached_origin(x, y, n_directions, return_tolerance):
            returned_to_origin = True
            # Snap to exact origin for saved paths/plots.
            x, y = 0.0, 0.0
            xs[-1], ys[-1] = x, y
            break

    steps_until_stop = len(xs) - 1
    return_time = float(steps_until_stop) if returned_to_origin else np.nan
    bbox_width = max_x - min_x
    bbox_height = max_y - min_y

    return {
        "xs": xs,
        "ys": ys,
        "steps_until_stop": steps_until_stop,
        "returned_to_origin": returned_to_origin,
        "censored": not returned_to_origin,
        "return_time": return_time,
        "max_distance": float(max_distance),
        "max_manhattan": float(max_manhattan),
        "bbox_width": float(bbox_width),
        "bbox_height": float(bbox_height),
        "bbox_area": float(bbox_width * bbox_height),
        "final_x": float(x),
        "final_y": float(y),
    }


# =========================
# Monte Carlo runners
# =========================


def run_unit_walk_trials(rng, n_trials, max_steps, paths_dir):
    """Run many 1D walks and return (summary_df, all_paths)."""
    trial_records = []
    all_paths = []

    for trial_idx in range(n_trials):
        walk = simulate_unit_walk_1d(rng=rng, max_steps=max_steps)
        path = walk["positions"]

        all_paths.append(path)
        save_1d_path_json(path, trial_idx, paths_dir)

        trial_records.append(
            {
                "trial_index": trial_idx,
                "steps_until_stop": walk["steps_until_stop"],
                "return_time": walk["return_time"],
                "returned_to_origin": walk["returned_to_origin"],
                "censored": walk["censored"],
                "max_abs_displacement": walk["max_abs_displacement"],
                "min_position": walk["min_position"],
                "max_position": walk["max_position"],
                "final_position": walk["final_position"],
            }
        )

    return pd.DataFrame(trial_records), all_paths


def run_cardinal_walk_trials(rng, n_trials, max_steps, paths_dir):
    """Run many mathemagicland 2D walks and return (summary_df, all_paths)."""
    trial_records = []
    all_paths = []

    for trial_idx in range(n_trials):
        walk = simulate_cardinal_walk_2d(rng=rng, max_steps=max_steps)
        path_pair = (walk["xs"], walk["ys"])

        all_paths.append(path_pair)
        save_2d_path_json(walk["xs"], walk["ys"], trial_idx, paths_dir)

        trial_records.append(
            {
                "trial_index": trial_idx,
                "steps_until_stop": walk["steps_until_stop"],
                "return_time": walk["return_time"],
                "returned_to_origin": walk["returned_to_origin"],
                "censored": walk["censored"],
                "max_distance": walk["max_distance"],
                "max_manhattan": walk["max_manhattan"],
                "bbox_width": walk["bbox_width"],
                "bbox_height": walk["bbox_height"],
                "bbox_area": walk["bbox_area"],
                "final_x": walk["final_x"],
                "final_y": walk["final_y"],
            }
        )

    return pd.DataFrame(trial_records), all_paths


def run_general_walk_trials(
    rng,
    n_trials,
    max_steps,
    n_directions,
    return_tolerance,
    round_decimals,
    paths_dir,
):
    """Run many N-direction walks and return (summary_df, all_paths)."""
    trial_records = []
    all_paths = []

    for trial_idx in range(n_trials):
        walk = simulate_general_walk(
            rng=rng,
            n_directions=n_directions,
            max_steps=max_steps,
            return_tolerance=return_tolerance,
            round_decimals=round_decimals,
        )
        path_pair = (walk["xs"], walk["ys"])

        all_paths.append(path_pair)
        save_2d_path_json(walk["xs"], walk["ys"], trial_idx, paths_dir)

        trial_records.append(
            {
                "trial_index": trial_idx,
                "n_directions": n_directions,
                "steps_until_stop": walk["steps_until_stop"],
                "return_time": walk["return_time"],
                "returned_to_origin": walk["returned_to_origin"],
                "censored": walk["censored"],
                "max_distance": walk["max_distance"],
                "max_manhattan": walk["max_manhattan"],
                "bbox_width": walk["bbox_width"],
                "bbox_height": walk["bbox_height"],
                "bbox_area": walk["bbox_area"],
                "final_x": walk["final_x"],
                "final_y": walk["final_y"],
            }
        )

    return pd.DataFrame(trial_records), all_paths


def split_paths_by_solution(all_paths, summary_df):
    """Split stored paths into solved vs censored groups."""
    paths_with_solution = [
        path
        for path, is_censored in zip(all_paths, summary_df["censored"])
        if not is_censored
    ]
    paths_without_solution = [
        path
        for path, is_censored in zip(all_paths, summary_df["censored"])
        if is_censored
    ]
    return paths_with_solution, paths_without_solution


# =========================
# Summary metrics
# =========================


def compute_unit_metrics(summary_df):
    completed = summary_df[~summary_df["censored"]]
    return {
        "completed_trials": int(len(completed)),
        "censored_trials": int(summary_df["censored"].sum()),
        "mean_return_time": (
            float(completed["return_time"].mean()) if len(completed) else float("nan")
        ),
        "variance_return_time": (
            float(completed["return_time"].var(ddof=1))
            if len(completed) > 1
            else float("nan")
        ),
        "mean_max_abs_displacement": float(summary_df["max_abs_displacement"].mean()),
    }


def compute_planar_metrics(summary_df, distance_col="max_distance"):
    completed = summary_df[~summary_df["censored"]]
    return {
        "completed_trials": int(len(completed)),
        "censored_trials": int(summary_df["censored"].sum()),
        "mean_return_time": (
            float(completed["return_time"].mean()) if len(completed) else float("nan")
        ),
        "mean_max_distance": float(summary_df[distance_col].mean()),
    }


# =========================
# Plot helpers
# =========================


def save_and_show(fig, out_path, dpi=150):
    fig.tight_layout()
    fig.savefig(out_path, dpi=dpi)
    plt.show()
    plt.close(fig)


def plot_histogram(
    values, out_path, title, xlabel, ylabel="Count", bins=30, color="tab:blue"
):
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.hist(list(values), bins=bins, color=color, edgecolor="white")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    save_and_show(fig, out_path)


def plot_single_walk_1d(positions, out_path, title):
    steps = np.arange(len(positions))
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.step(steps, positions, where="post", color="tab:blue", linewidth=2)
    ax.axhline(0, color="black", linewidth=1, alpha=0.8)
    ax.scatter([0], [0], color="green", s=70, marker="o", label="origin")
    ax.scatter(
        [steps[-1]], [positions[-1]], color="red", s=80, marker="X", label="stop point"
    )
    ax.set_title(title)
    ax.set_xlabel("Step number")
    ax.set_ylabel("Position")
    ax.legend(loc="best")
    save_and_show(fig, out_path)


def plot_single_walk_2d(xs, ys, out_path, title):
    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    ax.plot(xs, ys, color="tab:blue", linewidth=2, alpha=0.95)
    ax.scatter([0], [0], color="green", marker="*", s=180, label="origin")
    ax.scatter([xs[-1]], [ys[-1]], color="red", marker="X", s=120, label="stop point")
    ax.set_title(title)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect("equal", adjustable="box")
    ax.legend(loc="best")
    save_and_show(fig, out_path)


def _overlay_colors(n_paths):
    # Use distinct tab10 colors up to 10 trials, then fall back to blue.
    if n_paths <= 10:
        tab10 = list(plt.get_cmap("tab10").colors)
        return [tab10[i] for i in range(n_paths)]
    return ["tab:blue"] * n_paths


def _plot_1d_overlay_panel(ax, all_paths, title):
    colors = _overlay_colors(len(all_paths))
    for path, color in zip(all_paths, colors):
        steps = np.arange(len(path))
        ax.step(steps, path, where="post", color=color, alpha=0.45, linewidth=1.2)
        # Mark each endpoint so final states are easy to compare.
        ax.scatter(
            [steps[-1]],
            [path[-1]],
            color=color,
            s=28,
            marker="o",
            edgecolor="black",
            linewidth=0.4,
            zorder=3,
        )

    ax.axhline(0, color="black", linewidth=1)
    ax.set_title(title)
    ax.set_xlabel("Step number")
    ax.set_ylabel("Position")

    if not all_paths:
        ax.text(
            0.5,
            0.5,
            "No walks in this group",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=10,
            alpha=0.7,
        )


def plot_overlay_1d(all_paths, out_path, title):
    fig, ax = plt.subplots(figsize=(10, 5))
    _plot_1d_overlay_panel(ax, all_paths, title)
    save_and_show(fig, out_path)


def _plot_2d_overlay_panel(ax, all_paths, title):
    colors = _overlay_colors(len(all_paths))
    for (xs, ys), color in zip(all_paths, colors):
        ax.plot(xs, ys, color=color, alpha=0.45, linewidth=1.2)

    ax.scatter([0], [0], color="black", marker="*", s=120, label="origin")
    ax.set_title(title)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect("equal", adjustable="box")

    if not all_paths:
        ax.text(
            0.5,
            0.5,
            "No walks in this group",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=10,
            alpha=0.7,
        )
    ax.legend(loc="best")


def plot_overlay_1d_solution_split(
    paths_with_solution,
    paths_without_solution,
    out_path,
    left_title="1D Walks with Solution",
    right_title="Walks without a Solution",
    figure_title="Final Overlay",
):
    # If every walk returned, show only the solved panel.
    if paths_with_solution and not paths_without_solution:
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 5))
        _plot_1d_overlay_panel(ax, paths_with_solution, left_title)
        fig.suptitle(figure_title)
        save_and_show(fig, out_path)
        return

    # Keep both panels otherwise; empty groups display a placeholder message.
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(14, 5))
    _plot_1d_overlay_panel(axes[0], paths_with_solution, left_title)
    _plot_1d_overlay_panel(axes[1], paths_without_solution, right_title)
    fig.suptitle(figure_title)
    save_and_show(fig, out_path)


def plot_overlay_2d_solution_split(
    paths_with_solution,
    paths_without_solution,
    out_path,
    left_title="2D Walks with Solution",
    right_title="Walks without a Solution",
    figure_title="Final Overlay",
):
    # If every walk returned, show only the solved panel.
    if paths_with_solution and not paths_without_solution:
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(7, 7))
        _plot_2d_overlay_panel(ax, paths_with_solution, left_title)
        fig.suptitle(figure_title)
        save_and_show(fig, out_path)
        return

    # Keep both panels otherwise; empty groups display a placeholder message.
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(13, 6))
    _plot_2d_overlay_panel(axes[0], paths_with_solution, left_title)
    _plot_2d_overlay_panel(axes[1], paths_without_solution, right_title)
    fig.suptitle(figure_title)
    save_and_show(fig, out_path)
