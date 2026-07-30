from typing import Optional

import multiprocessing as mp
import matplotlib.pyplot as plt
import numpy as np
import queue

from maze_core import OccupancyGrid, EntityType, GameState

_plot_proc: mp.Process | None = None
_plot_q: Optional[mp.Queue] = None

def _plotter_main(q: mp.Queue):
    import matplotlib.pyplot as plt
    plt.ion()
    fig, ax = plt.subplots()
    im = None
    agent_pt = None
    current_extent = None

    while True:
        msg = q.get()
        if msg is None:
            break

        grid_data, agent_position, world_w, world_h = msg
        extent = (-world_w/2, world_w/2, -world_h/2, world_h/2)

        if im is None or agent_pt is None:
            im = ax.imshow(grid_data, origin="lower", extent=extent)
            agent_pt, = ax.plot([agent_position[0]], [agent_position[1]], 'ro', markersize=2)
            ax.set_xlabel("x"); ax.set_ylabel("y")
        else:
            if extent != current_extent:
                im.set_extent(extent)
            im.set_data(grid_data)
            agent_pt.set_data([agent_position[0]], [agent_position[1]])

        ax.set_ylim(extent[3], extent[2])  # keep Y inverted
        current_extent = extent

        fig.canvas.draw_idle()
        fig.canvas.flush_events()

    plt.close(fig)


def _ensure_plotter():
    global _plot_proc, _plot_q
    if _plot_proc is None or not _plot_proc.is_alive():
        _plot_q = mp.Queue()
        _plot_proc = mp.Process(target=_plotter_main, args=(_plot_q,), daemon=True)
        _plot_proc.start()

def stop_plotter():
    global _plot_proc, _plot_q
    if _plot_proc is None or _plot_q is None:
        return
    try:
        _plot_q.put_nowait(None)
    except Exception:
        pass
    _plot_proc.join(timeout=1.0)
    _plot_proc = None
    _plot_q = None


def render(state: GameState, occupancy_grid: OccupancyGrid, special_cells: Optional[list[tuple[int, int]]] = None):
    _ensure_plotter()
    assert _plot_q is not None

    if special_cells is None:
        special_cells = []

    grid_data = np.zeros((occupancy_grid.height, occupancy_grid.width, 3), dtype=float)

    for i in range(occupancy_grid.width):
        for j in range(occupancy_grid.height):
            cell = occupancy_grid[i, j]
            p_free, p_wall, p_flag, p_capture_point = cell.probabilities()

            if cell.assignment == EntityType.Wall:
                grid_data[j, i] = (0, 0, 0)          # black
            elif cell.assignment == EntityType.Flag:
                grid_data[j, i] = (1, 0.75, 0.8)     # pink
            elif cell.assignment == EntityType.CapturePoint:
                grid_data[j, i] = (0, 1, 1)          # cyan
            else:
                grid_data[j, i] = (p_free, p_free, p_free)  # gray

    for i, j in special_cells:
        if 0 <= i < occupancy_grid.width and 0 <= j < occupancy_grid.height:
            grid_data[j, i] = (0, 1, 0)  # green

    agent_position = state.agent.position
    world_w = state.world_width
    world_h = state.world_height

    try:
        _plot_q.put_nowait((grid_data, agent_position, world_w, world_h))
    except queue.Full:
        try:
            _plot_q.get_nowait()
        except queue.Empty:
            pass
        _plot_q.put_nowait((grid_data, agent_position, world_w, world_h))
