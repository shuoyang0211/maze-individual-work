def line_between(start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
    """
    Bresenham's Line Algorithm to get the grid cells between two points.
    Computes the cells that a line from start to end would pass through the grid.

    Parameters:
        `start`: The starting grid cell.
        `end`: The ending grid cell.

    Returns:
        A list of grid cells that the line passes through, including
        start and end.
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
