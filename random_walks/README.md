# Stochastic Random Walks: Time to Return Home

I got the idea from [mathemagicland](www.instagram.com/mathemagiclandinsta)'s random walk [video](https://www.instagram.com/p/DW2BveQklDj/)!

This is a huge concept in stochastic processes and fundamental for understanding diffusion, recurrence, and hitting times in random systems, with applications ranging from physics and finance to algorithms and network theory.

The biggest question we'll ask is:

> **How long does it take to come back home?**

---

## Quick Demo Workflow

Each notebook in this folder is now set up as a short demo:

1. Change a few config values near the top.
2. Run all cells top to bottom.
3. Inspect saved images/CSV files under `outputs/...`.

Main knobs to play with:

- `RANDOM_SEED`
- `N_TRIALS`
- `MAX_STEPS`
- `N_DIRECTIONS` (general notebook only)

---

## The core problem

We start at the origin and take random steps. Define the position after $n$ steps:

$$
S_n = X_1 + X_2 + \cdots + X_n
$$

We are interested in the **first return time**:

$$
T = \inf \{ n \ge 1 : S_n = 0 \}
$$

This is the number of steps it takes to return to the origin *for the first time* after leaving it.

All simulations in this project are estimating properties of $T$.

---

## Novelty

Random walks have two competing behaviors:

- They spread out over time  
- But they also keep coming back

In 1D and 2D:

- The walk returns to the origin with probability 1  
- But the time it takes behaves in a very surprising way:

$$
\mathbb{E}[T] = \infty
$$

So:
- You will almost surely return  
- But there is no finite average return time

This happens because of heavy tails: most walks return quickly, but some take extremely long.

---

## Case 1: 1D unit random walk

### Model

- Start at $0$
- Each step:
  - $+1$ with probability $1/2$
  - $-1$ with probability $1/2$

### Return behavior

- Guaranteed to return eventually  
- But expected return time:

$$
\mathbb{E}[T] = \infty
$$

### Time complexity interpretation

Think of each simulation as an algorithm that runs until return.

- **Best case:**  
  Return in 2 steps  
  (right, then left or vice versa)  
  → $O(1)$

- **Typical behavior:**  
  Often returns relatively quickly, but highly variable  

- **Worst case:**  
  Arbitrarily large number of steps  
  → unbounded (no finite upper limit)

- **Expected time:**  
  Infinite (due to rare extremely long walks)

---

## Case 2: 2D rotational walk

This is the idea that [mathemagicland](https://www.instagram.com/mathemagiclandinsta) presents. A walk where we take a step in a random cardinal direction.

### Model

Each step chooses one of:

- $(1,0)$  
- $(0,1)$  
- $(-1,0)$  
- $(0,-1)$  

with equal probability.

### Return behavior

- Still guaranteed to return  
- Still:

$$
\mathbb{E}[T] = \infty
$$

### Time complexity interpretation

- **Best case:**  
  Return in 2 steps (go out, come back)  
  → $O(1)$

- **Typical behavior:**  
  Takes longer than 1D on average (more directions to wander)

- **Worst case:**  
  Unbounded  

- **Expected time:**  
  Infinite  

---

## Case 3: General $N$-direction walk

### Model

At each step, choose uniformly from:

$$
\theta = \frac{2\pi k}{N}, \quad k = 0, 1, \dots, N-1
$$

and move one unit in that direction.

### Return behavior

- For $N \ge 3$ (2D walks), still recurrent  
- So:

$$
\mathbb{E}[T] = \infty
$$

### Time complexity interpretation

- **Best case:**  
  Immediate reversal → $O(1)$

- **Typical behavior:**  
  More directions ⇒ more wandering ⇒ longer return times

- **Worst case:**  
  Unbounded  

- **Expected time:**  
  Infinite  

---

## What the simulations actually compute

In practice, we cannot simulate infinitely long walks.

Each notebook introduces a limit:

- `MAX_STEPS`

Current notebook defaults:

- `RANDOM_SEED = 42`
- `N_TRIALS = 10`
- `MAX_STEPS = 20_000`
- `N_DIRECTIONS = 8` (general notebook)

So we compute a **truncated return time**:

$$
T_{\text{trunc}} = \min(T, \text{MAX\_STEPS})
$$

This means:

- If the walk returns → record actual return time  
- If not → mark as incomplete (censored)

So the simulations estimate:

$$
\mathbb{E}[\min(T, \text{MAX\_STEPS})]
$$

which is finite and observable.

---

## What you should expect to see

Across all notebooks:

### 1. Many short walks
- Quick returns (small $T$)

### 2. Some medium walks
- Wandering before returning

### 3. Rare very long walks
- These dominate the average
- These are why $\mathbb{E}[T] = \infty$

### 4. Heavy-tailed distributions
- Histograms will have long right tails
- Increasing `MAX_STEPS` increases observed averages

---

## Visualization outputs

Each notebook generates:

- A **single walk** (stops at first return)
- Monte Carlo statistics:
  - return times
  - max distance
- Histograms of:
  - return time
  - max displacement
- A final **overlay plot**:
  - 1D notebook: all walks overlaid in one panel
  - 2D notebooks: two side-by-side panels
    - left: walks with a solution (returned to origin)
    - right: walks without a solution (censored)

The overlay plots visually show:

- Most paths stay near the origin  
- Some paths wander far before returning  
- Color rule in current notebooks:
  - if there are 10 walks or fewer, each walk gets a distinct `tab10` color
  - if there are more than 10 walks, all walks are drawn in blue

### Sample output figures

These images are generated by running the notebooks in this folder.

#### 1D unit walk

![1D single walk](outputs/unit_walk_1D/single_walk.png)
![1D overlay walks](outputs/unit_walk_1D/overlay_walks.png)

#### Mathemagicland 2D walk

![2D single walk](outputs/mathemagicland_solution/single_walk.png)
![2D return-time histogram](outputs/mathemagicland_solution/return_time_histogram.png)

#### General N-direction walk

![General walk single](outputs/general_walk_solution/single_walk.png)
![General walk overlay](outputs/general_walk_solution/overlay_walks.png)

---

## Key takeaway

Random walks are not just about where you end up, but how long it takes to return.

Even though:

$$
\mathbb{E}[\text{position}] = 0,
\quad
\mathbb{E}[\text{distance}^2] = n
$$

the return time behaves very differently:

$$
\mathbb{E}[T] = \infty
$$

So the system is:

- **Stable in position**
- **Unstable in time**

You always come back home.  
You just don’t know how long it will take.
