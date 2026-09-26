# NeuroTraffic

A top-down traffic simulator where neural networks learn to control traffic lights.

## Features

- **2D Pygame simulation** with a 4×4 road grid
- **Rule-based cars** with pathfinding, collision avoidance, and traffic law adherence
- **Traffic lights** — fixed-timer or neural-network controlled
- **Genetic algorithm** training to optimize traffic flow
- **Real-time metrics** dashboard (travel time, wait time, congestion, etc.)
- **Debug overlays** — node IDs, queue lengths, congestion heatmap
- **Save/load** trained brain models

## Quick Start

Requires Python 3.9+.

```bash
python -m venv .venv
# Windows:      .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -e ".[dev]"      # or: pip install -r requirements.txt
python -m neurotraffic.main  # or just: neurotraffic
```

### Headless training

Train without opening a window (much faster), then load the result in the app with **L**:

```bash
python -m neurotraffic.train --generations 20 --save   # --seed N for reproducible runs
```

### Tests

```bash
pytest
```

## Controls

| Key | Action |
|-------|----------------------|
| Space | Pause / Resume |
| R | Reset simulation |
| T | Toggle training mode |
| D | Toggle debug overlay |
| H | Toggle heatmap |
| 1 | Speed 1× |
| 2 | Speed 3× |
| 3 | Speed 10× |
| S | Save best brain |
| L | Load best brain |
| F | Back to fixed-timer lights |
| N | Next generation (training) |
| Esc | Quit |

## Architecture

```
neurotraffic/
  main.py              # Entry point & Pygame loop
  train.py             # Headless training CLI
  core/                # Simulation engine, config, clock
  world/               # Road network graph, intersections, traffic lights
  vehicles/            # Cars, pathfinding, routes
  ai/                  # Brain interface, neural nets, genetic trainer
  metrics/             # Performance tracking
  rendering/           # Pygame drawing, dashboard, debug overlay
  persistence/         # Save/load models and experiments
  data/                # Configs, saved models, experiment logs
tests/                 # pytest suite
```

## Training

Press **T** to enter training mode. The genetic algorithm evaluates each brain by running a full simulation and scoring it on:

- Cars completed (+)
- Average travel time (−)
- Average wait time (−)
- Congestion score (−)
- Light switch frequency (−)

The best brains survive and mutate into the next generation. Press **S** to save the best brain at any time.

## Version

0.1.0 — MVP
