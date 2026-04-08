# Stochastic Random Walks

I actually got the idea from [mathemagicland](www.instagram.com/mathemagiclandinsta)'s random walk [video](https://www.instagram.com/p/DW2BveQklDj/)!

A **random walk** is a simple but powerful idea: you start at some point, and at each step you move in a randomly chosen direction. The path looks chaotic, but when you analyze it mathematically, very clean patterns emerge.

Random walks appear everywhere: particle motion, diffusion, stock prices, search algorithms, and more.

---

## The core idea

A random walk is just a sum of independent steps.

If we write the position after $n$ steps as

$$
S_n = X_1 + X_2 + \cdots + X_n,
$$

where each $X_k$ is a random step, then everything about the walk comes from understanding a **single step**.

Two key facts drive everything:

- **Linearity of expectation**:
  $$
  \mathbb{E}[S_n] = n \cdot \mathbb{E}[X_1]
  $$

- **Variance adds for independent steps**:
  $$
  \mathrm{Var}(S_n) = n \cdot \mathrm{Var}(X_1)
  $$

So the entire analysis reduces to:
1. What is the average of one step?
2. How much does one step spread things out?

---

## The simplest example: 1D unit walk

You start at

$$
X_0 = 0
$$

and at each step:

- move $+1$ with probability $1/2$
- move $-1$ with probability $1/2$

Let the step be

$$
\xi_k =
\begin{cases}
+1 & \text{with probability } 1/2 \\
-1 & \text{with probability } 1/2
\end{cases}
$$

Then

$$
X_n = \sum_{k=1}^n \xi_k.
$$

### Expected position

Each step is perfectly symmetric, so there is no preferred direction:

$$
\mathbb{E}[\xi_k] = 0
\quad \Rightarrow \quad
\mathbb{E}[X_n] = 0.
$$

On average, the walker stays centered.

### Variance

Each step always has magnitude 1, so

$$
\mathbb{E}[\xi_k^2] = 1,
\quad
\mathrm{Var}(\xi_k) = 1.
$$

Since variance adds:

$$
\mathrm{Var}(X_n) = n.
$$

### Result

$$
\boxed{
\mathbb{E}[X_n] = 0,
\quad
\mathrm{Var}(X_n) = n
}
$$

So the walk does not drift, but it spreads out like $\sqrt{n}$.

---

## The 2D rotational walk (from the video)

Now instead of left/right, each step chooses one of four directions:

- $0^\circ$ → $(1,0)$  
- $90^\circ$ → $(0,1)$  
- $180^\circ$ → $(-1,0)$  
- $270^\circ$ → $(0,-1)$  

each with probability $1/4$.

Let each step be $V_k$, and define

$$
S_n = \sum_{k=1}^n V_k = (X_n, Y_n).
$$

### Expected position

Again, the system is perfectly symmetric:

$$
\mathbb{E}[V_k] = (0,0)
\quad \Rightarrow \quad
\mathbb{E}[S_n] = (0,0).
$$

No direction is favored.

### Variance (coordinate-wise)

Look at the $x$-coordinate of one step:

- $+1$ with probability $1/4$
- $-1$ with probability $1/4$
- $0$ with probability $1/2$

So:

$$
\mathbb{E}[X_1] = 0,
\quad
\mathbb{E}[X_1^2] = \frac{1}{2},
\quad
\mathrm{Var}(X_1) = \frac{1}{2}.
$$

Same for $Y_1$.

By independence:

$$
\mathrm{Var}(X_n) = \frac{n}{2},
\quad
\mathrm{Var}(Y_n) = \frac{n}{2}.
$$

### Distance from the origin

The squared distance is:

$$
\|S_n\|^2 = X_n^2 + Y_n^2.
$$

Taking expectation:

$$
\mathbb{E}[\|S_n\|^2]
= \mathrm{Var}(X_n) + \mathrm{Var}(Y_n)
= \frac{n}{2} + \frac{n}{2}
= n.
$$

### Result

$$
\boxed{
\mathbb{E}[S_n] = (0,0),
\quad
\mathbb{E}[\|S_n\|^2] = n
}
$$

Each step contributes exactly one unit of expected squared displacement.

---

## A cleaner view: complex numbers

We can represent directions as complex numbers:

$$
1,\quad i,\quad -1,\quad -i.
$$

Each step is a random variable $Z_k$ chosen uniformly from these.

Then:

$$
W_n = \sum_{k=1}^n Z_k.
$$

Now everything becomes simpler:

- symmetry ⇒ $\mathbb{E}[Z_k] = 0$
- unit length ⇒ $|Z_k| = 1$

So:

$$
\mathbb{E}[W_n] = 0,
\quad
\mathbb{E}[|W_n|^2] = n.
$$

---

## Generalization: $N$ equally spaced directions

The 4-direction walk is just the case $N = 4$.

Now suppose we allow $N$ equally spaced directions:

$$
0,\; \frac{2\pi}{N},\; \frac{4\pi}{N},\; \dots,\; \frac{2\pi(N-1)}{N}.
$$

Each step is

$$
Z_k = e^{2\pi i J_k / N},
$$

where $J_k$ is uniform on $\{0,1,\dots,N-1\}$.

### Expected value

The average of all $N$-th roots of unity is zero:

$$
\mathbb{E}[Z_k] = 0
\quad \Rightarrow \quad
\mathbb{E}[W_n] = 0.
$$

### Mean squared distance

Each step still has length 1:

$$
|Z_k|^2 = 1.
$$

So:

$$
\mathbb{E}[|W_n|^2] = n.
$$

### Coordinate variances

For $N \ge 3$, the walk is rotationally symmetric, so variance splits evenly:

$$
\mathrm{Var}(X_n) = \mathrm{Var}(Y_n) = \frac{n}{2}.
$$

---

## Final takeaway

A random walk may look unpredictable, but its large-scale behavior is governed by a few simple rules.

As long as:
- steps are independent  
- steps are unbiased (mean 0)  
- steps have unit length  

then:

$$
\boxed{
\mathbb{E}[\text{position}] = 0,
\quad
\mathbb{E}[\text{distance}^2] = n
}
$$

So even though every path is random, the overall behavior is not. The walk stays centered, and its spread grows in a perfectly predictable way.