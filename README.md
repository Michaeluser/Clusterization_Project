# Agglomerative Clusterization

A Python implementation of **agglomerative (bottom-up) hierarchical clustering** applied to a large set of randomly generated 2D points. Cluster centers can be computed using either a **centroid** or **medoid** strategy. Distance calculations are offloaded to a compiled C library for performance. Results are visualized frame-by-frame in Pygame with a Tkinter slider.

## How It Works

10,000 points are generated — 20 anchor points placed across the map, with the rest distributed around them via random offsets. A pairwise Manhattan distance matrix is then computed.

Each iteration of the main loop finds the closest pair in the distance matrix and merges them into a new cluster. The cluster center is recomputed as either a centroid (mean position) or a medoid (real point nearest to the centroid). Merging continues as long as the average intra-cluster distance stays below a configurable threshold (`avg_idc`). Once a cluster exceeds that threshold it is flagged as complete and removed from further consideration.

Intermediate cluster states are saved as JSON files and loaded by `illustrate.py` for playback.

## Project Structure

```
clusterization.py     # Main clustering algorithm
illustrate.py         # Pygame/Tkinter visualization
functions.c           # C implementation of distance calculations
functions.h           # Header file
functions.so          # Compiled shared library (Linux)
functions.dll         # Compiled shared library (Windows)
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `medoid` | `True` | Use medoid (`True`) or centroid (`False`) for cluster center |
| `points_amount` | `10000` | Number of points to generate |
| `avg_idc` | `250` | Max average intra-cluster distance before a cluster is sealed |
| `t_md` | `True` | Use C library for distance computation (faster) |

## Requirements

```bash
pip install numpy cffi pygame Pillow
```

The C library must be compiled before running:

```bash
gcc -shared -fPIC -o functions.so functions.c -lm   # Linux
```

## Usage

```bash
python clusterization.py   # run clustering, outputs pr_points.json and cr_info*.json
python illustrate.py        # visualize results
``
