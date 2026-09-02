from maze_core import Position


def position_to_grid_cell(position: Position, cell_size: float, world_width: float, world_height: float) -> tuple[int, int]:
    """
    Converts a world position to grid cell coordinates.
    Assumes the world is centered at (0, 0) and extends to (world_width/2, world_height/2) in all directions.

    Parameters:
        position (Position): The world position to convert.
        cell_size (float): The size of each grid cell.
        world_width (float): The total width of the world.
        world_height (float): The total height of the world.

    Returns:
        tuple[int, int]: The grid cell coordinates (x, y).
    """

    grid_x = int((position[0] + world_width / 2) // cell_size)
    grid_y = int((position[1] + world_height / 2) // cell_size)

    grid_x = max(0, min(grid_x, int(world_width // cell_size) - 1))
    grid_y = max(0, min(grid_y, int(world_height // cell_size) - 1))

    return (grid_x, grid_y)

def line_between(start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
    """
    Bresenham's Line Algorithm to get the grid cells between two points.
    Computes the cells that a line from start to end would pass through the grid.

    Parameters:
        start (tuple[int, int]): The starting grid cell (x, y).
        end (tuple[int, int]): The ending grid cell (x, y).

    Returns:
        list[tuple[int, int]]: A list of grid cells (x, y) that the line passes through including start and end.
    """
    x0, y0 = start
    x1, y1 = end
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    points = []
    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

    return list(dict.fromkeys(points))