from pathlib import Path
import json
import math
from typing import Dict, Iterable, List, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


CARDINAL_STEPS = np.array(
    [
        [1, 0],
        [0, 1],
        [-1, 0],
        [0, -1],
    ],
    dtype=int,
)


def ensure_output_dirs(base_output_dir: Path) -> Tuple[Path, Path]:
    """Create output and paths directories and return both."""
    paths_dir = base_output_dir / "paths"
    base_output_dir.mkdir(parents=True, exist_ok=True)
    paths_dir.mkdir(parents=True, exist_ok=True)
    return base_output_dir, paths_dir


def save_json(payload: Dict[str, object], out_path: Path) -> Path:
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f)
    return out_path


def save_1d_path_json(path_positions: Sequence[int], trial_index: int, paths_dir: Path) -> Path:
    payload = {
        "trial_index": int(trial_index),
        "positions": [int(v) for v in path_positions],
    }
    return save_json(payload, paths_dir / f"trial_{trial_index:04d}.json")


def save_2d_path_json(xs: Sequence[float], ys: Sequence[float], trial_index: int, paths_dir: Path) -> Path:
    payload = {
        "trial_index": int(trial_index),
        "x": [float(v) for v in xs],
        "y": [float(v) for v in ys],
    }
    return save_json(payload, paths_dir / f"trial_{trial_index:04d}.json")


def simulate_unit_walk_1d(rng: np.random.Generator, max_steps: int) -> Dict[str, object]:
    position = 0
    positions: List[int] = [position]

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


def simulate_cardinal_walk_2d(rng: np.random.Generator, max_steps: int) -> Dict[str, object]:
    x, y = 0, 0
    xs: List[int] = [x]
    ys: List[int] = [y]

    min_x = max_x = x
    min_y = max_y = y
    max_distance = 0.0
    max_manhattan = 0
    returned_to_origin = False

    for _ in range(max_steps):
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


def get_direction_vectors(n_directions: int) -> np.ndarray:
    if n_directions < 2:
        raise ValueError("N_DIRECTIONS must be >= 2")

    if n_directions == 2:
        return np.array([[1.0, 0.0], [-1.0, 0.0]], dtype=float)

    if n_directions == 4:
        return CARDINAL_STEPS.astype(float)

    angles = 2.0 * np.pi * np.arange(n_directions) / n_directions
    return np.column_stack((np.cos(angles), np.sin(angles)))


def reached_origin(x: float, y: float, n_directions: int, tolerance: float) -> bool:
    if n_directions in (2, 4):
        return (x == 0.0) and (y == 0.0)
    return math.hypot(x, y) <= tolerance


def simulate_general_walk(
    rng: np.random.Generator,
    n_directions: int,
    max_steps: int,
    return_tolerance: float,
    round_decimals: int,
) -> Dict[str, object]:
    vectors = get_direction_vectors(n_directions)

    x, y = 0.0, 0.0
    xs: List[float] = [x]
    ys: List[float] = [y]

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


def save_and_show(fig: plt.Figure, out_path: Path, dpi: int = 150) -> None:
    fig.tight_layout()
    fig.savefig(out_path, dpi=dpi)
    plt.show()
    plt.close(fig)


def plot_histogram(
    values: Iterable[float],
    out_path: Path,
    title: str,
    xlabel: str,
    ylabel: str = "Count",
    bins: int = 30,
    color: str = "tab:blue",
) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.hist(list(values), bins=bins, color=color, edgecolor="white")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    save_and_show(fig, out_path)


def plot_single_walk_1d(positions: Sequence[int], out_path: Path, title: str) -> None:
    steps = np.arange(len(positions))
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(steps, positions, color="tab:blue", linewidth=2)
    ax.axhline(0, color="black", linewidth=1, alpha=0.8)
    ax.scatter([0], [0], color="green", s=70, marker="o", label="origin")
    ax.scatter([steps[-1]], [positions[-1]], color="red", s=80, marker="X", label="stop point")
    ax.set_title(title)
    ax.set_xlabel("Step number")
    ax.set_ylabel("Position")
    ax.legend(loc="best")
    save_and_show(fig, out_path)


def plot_overlay_1d(all_paths: Sequence[Sequence[int]], out_path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    if len(all_paths) <= 10:
        tab10 = list(plt.get_cmap("tab10").colors)
        colors = [tab10[i] for i in range(len(all_paths))]
    else:
        colors = ["tab:blue"] * len(all_paths)

    for path, color in zip(all_paths, colors):
        steps = np.arange(len(path))
        ax.plot(steps, path, color=color, alpha=0.45, linewidth=1.2)

    ax.axhline(0, color="black", linewidth=1)
    ax.set_title(title)
    ax.set_xlabel("Step number")
    ax.set_ylabel("Position")
    save_and_show(fig, out_path)


def plot_single_walk_2d(
    xs: Sequence[float],
    ys: Sequence[float],
    out_path: Path,
    title: str,
) -> None:
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


def plot_overlay_2d(
    all_paths: Sequence[Tuple[Sequence[float], Sequence[float]]],
    out_path: Path,
    title: str,
) -> None:
    fig, ax = plt.subplots(figsize=(7, 7))
    if len(all_paths) <= 10:
        tab10 = list(plt.get_cmap("tab10").colors)
        colors = [tab10[i] for i in range(len(all_paths))]
    else:
        colors = ["tab:blue"] * len(all_paths)

    for (xs, ys), color in zip(all_paths, colors):
        ax.plot(xs, ys, color=color, alpha=0.45, linewidth=1.2)

    ax.scatter([0], [0], color="black", marker="*", s=160, label="origin")
    ax.set_title(title)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect("equal", adjustable="box")
    ax.legend(loc="best")
    save_and_show(fig, out_path)


def save_summary_csv(summary_df: pd.DataFrame, out_path: Path) -> Path:
    summary_df.to_csv(out_path, index=False)
    return out_path
