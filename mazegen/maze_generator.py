import sys
import random
import time
from collections.abc import Callable, Iterator
from typing import Optional
from .maze_config import MazeConfig
from heapq import heappush, heappop


class MazeGenerator:
    def __init__(self, width: int, height: int,
                 entry: tuple[int, int], exit: tuple[int, int],
                 seed: int | None = None, perfect: bool = True,
                 output_file: str = "maze.txt") -> None:
        """ initializes the MazeGenerator with the given parameters,

        Args:
            width (int): the width of the maze to generate
            height (int): the height of the maze to generate
            entry (tuple[int, int]): the coordinates of the entry point (x,y)
            exit (tuple[int, int]): the coordinates of the exit point (x,y)
            seed (int | None, optional): the seed for
            the random number generator,
            if None, it will be set to the current time.
            Defaults to None.
            perfect (bool, optional): whether to generate
            a perfect maze (no loops),
            or a non-perfect maze (with loops). Defaults to True.
            output_file (str, optional): the file to write the maze
            to when finished. Defaults to "maze.txt".
            already_valid (bool, optional): whether
            the parameters have already been validated,
            this is used when creating a MazeGenerator
            from a MazeConfig object,
            to avoid validating the parameters twice. Defaults to False.
        """
        self.width: int = width
        self.height: int = height
        self.maze: list[list[int]] = []
        self.entry: tuple[int, int] = entry
        self.exit: tuple[int, int] = exit
        self.path: str = ""
        self.output_file: str = output_file
        self.perfect: bool = perfect
        self.seed = seed
        self.solution: str = ""
        self.position: tuple[int, int] = entry
        if seed is None:
            self.seed = int(time.time())
        random.seed(self.seed)

    @staticmethod
    def new(config: MazeConfig) -> 'MazeGenerator':
        """ creates a MazeGenerator from a configuration object,
        which should have the same attributes as the constructor parameters

        Args:
            config ('MazeConfig'): a configuration object with attributes:
            width, height, entry, exit, perfect, seed, output_file

        Returns:
            MazeGenerator: the generated maze
        """
        return MazeGenerator(
            width=config.width,
            height=config.height,
            entry=config.entry,
            exit=config.exit,
            perfect=config.perfect,
            seed=config.seed,
            output_file=config.output_file
        )

    def write_to_file(self, filename: str) -> None:
        """ writes the generated maze to a file in the specified format,

        Args:
            filename (str): the name of the file to write the maze to
        """
        with open(filename, 'w') as f:
            for row in self.maze:
                line = ''.join(f"{cell & 0b1111:X}" for cell in row)
                f.write(line + '\n')
            f.write("\n")
            f.write(f"{self.entry[0]},{self.entry[1]}\n")
            f.write(f"{self.exit[0]},{self.exit[1]}\n")
            f.write(self.solution + '\n')

    def initialize(self) -> None:
        """generates the maze by initializing it,
        adding the 42 pattern, marking the entry and exit,
        """
        self.maze = [
            [15 for _ in range(self.width)]
            for _ in range(self.height)
        ]
        for i in range(self.width):
            self.maze[0][i] |= 0b0001
            self.maze[self.height - 1][i] |= 0b0100
        for i in range(self.height):
            self.maze[i][0] |= 0b1000
            self.maze[i][self.width - 1] |= 0b0010

        self.maze[self.entry[1]][self.entry[0]] |= 0b10000000
        self.maze[self.entry[1]][self.entry[0]] |= 0b100000
        self.maze[self.exit[1]][self.exit[0]] |= 0b01000000
        self._add_42_pattern()

    def wilson_algo(self) -> None:
        """ generates the maze using Wilson's algorithm,
        which is a randomized algorithm
        """
        def wilson_path(start: tuple[int, int]) -> list[tuple[int, int]]:
            """ performs a random walk from the start point
            until it reaches a cell that is already part of the maze,

            Args:
                start (tuple[int, int]): the starting point of the random walk

            Returns:
                list[tuple[int, int]]: the path taken by the random walk,
                which will be carved into the maze
            """
            path: list[tuple[int, int]] = [start]
            self.maze[start[1]][start[0]] |= 0b10000
            p = start

            def random_neighbor(p: tuple[int, int]) -> tuple[int, int]:
                neighbors = []
                if (p[1] > 0
                        and self.maze[p[1] - 1][p[0]] >> 4 != 0b1111):
                    neighbors.append((p[0], p[1] - 1))
                if (p[0] < self.width - 1
                        and self.maze[p[1]][p[0] + 1] >> 4 != 0b1111):
                    neighbors.append((p[0] + 1, p[1]))
                if (p[1] < self.height - 1
                        and self.maze[p[1] + 1][p[0]] >> 4 != 0b1111):
                    neighbors.append((p[0], p[1] + 1))
                if (p[0] > 0
                        and self.maze[p[1]][p[0] - 1] >> 4 != 0b1111):
                    neighbors.append((p[0] - 1, p[1]))
                return random.choice(neighbors)

            while True:
                p = random_neighbor(p)
                if p in path:
                    loop_start = path.index(p)
                    to_remove = path[loop_start + 1:]
                    path = path[:loop_start + 1]
                    for cell in to_remove:
                        self.maze[cell[1]][cell[0]] &= ~0b10000

                elif self.maze[p[1]][p[0]] >> 5 & 1:
                    path.append(p)
                    return path

                else:
                    path.append(p)
                    self.maze[p[1]][p[0]] |= 0b10000

        def carve_path(path: list[tuple[int, int]]) -> None:
            """ carves the path taken by the random walk
            into the maze by opening the walls

            Args:
                path (list[tuple[int, int]]): the path to carve into the maze
            """
            def get_neighbors(p: tuple[int, int]) -> list[tuple[int, int]]:
                """ returns the neighboring cells of a given cell
                that are not completely closed off,

                Args:
                    p (tuple[int, int]): the cell to get the neighbors of

                Returns:
                    list[tuple[int, int]]: the neighboring cells that
                    are not completely closed off
                """
                neighbors = []
                if p[1] > 0 and self.maze[p[1] - 1][p[0]] >> 4 != 0:
                    neighbors.append((p[0], p[1] - 1))
                if (p[0] < self.width - 1
                        and self.maze[p[1]][p[0] + 1] >> 4 != 0):
                    neighbors.append((p[0] + 1, p[1]))
                if (p[1] < self.height - 1
                        and self.maze[p[1] + 1][p[0]] >> 4 != 0):
                    neighbors.append((p[0], p[1] + 1))
                if p[0] > 0 and self.maze[p[1]][p[0] - 1] >> 4 != 0:
                    neighbors.append((p[0] - 1, p[1]))
                return neighbors

            def is_safe_to_break(p: tuple[int, int]) -> bool:
                """ checks if it's safe to break a wall at
                the given cell without creating a loop,

                Args:
                    p (tuple[int, int]): the cell to check

                Returns:
                    bool: True if safe to break a wall at the given cell,
                    False otherwise
                """
                neighbors = get_neighbors(p)
                if len(neighbors) != 4:
                    return False
                for n in neighbors:
                    if self.maze[n[1]][n[0]] >> 4 == 0b1111:
                        return False
                return True

            for i in range(len(path) - 1):
                p1, p2 = path[i], path[i + 1]
                self.maze[p1[1]][p1[0]] &= ~0b10000
                if p1[0] == p2[0]:
                    if p1[1] < p2[1]:
                        self._change_wall(p1, "S", "open")
                    else:
                        self._change_wall(p1, "N", "open")
                else:
                    if p1[0] < p2[0]:
                        self._change_wall(p1, "E", "open")
                    else:
                        self._change_wall(p1, "W", "open")
            if (is_safe_to_break(p1)
                    and random.random() < 0.5
                    and not self.perfect):
                to_break = "NESW"
                self._change_wall(p1, random.choice(to_break), "open")

        unvisited = set((x, y) for x in range(self.width)
                        for y in range(self.height)
                        if not self.maze[y][x] >> 4 & 0b1)
        rpoint: tuple[int, int] = random.choice(list(unvisited))
        while True:
            if not unvisited:
                break
            while rpoint not in unvisited:
                rpoint = random.choice(list(unvisited))
            new_connected = wilson_path(rpoint)
            for point in new_connected:
                self.maze[point[1]][point[0]] |= 0b100000
            unvisited -= set(new_connected)
            carve_path(new_connected)

        for y in range(self.height):
            for x in range(self.width):
                self.maze[y][x] &= ~0b100000

        self.maze[self.entry[1]][self.entry[0]] |= 0b10000000
        self.maze[self.exit[1]][self.exit[0]] |= 0b01000000

        for y in range(self.height):
            for x in range(self.width):
                if self.maze[y][x] & 0b1111 == 0b1111:
                    self.maze[y][x] = 0b11111111

    def _add_42_pattern(self) -> None:
        """closes the walls in a pattern that resembles
        the 42 logo in the center of the maze
        """
        l42: list[tuple[int, int]] = [
            (0, 0), (0, 1), (0, 2), (1, 2),
            (2, 2), (2, 3), (2, 4), (2, 1),
            (2, 0), (4, 0), (5, 0), (6, 0),
            (6, 1), (6, 2), (5, 2), (4, 2),
            (4, 3), (4, 4), (5, 4), (6, 4)]

        for p in l42:
            p_offset: tuple[int, int] = (
                p[0] + round(self.width / 2) - 3,
                p[1] + round(self.height / 2) - 3
                )
            if p_offset in (self.entry, self.exit):
                raise ValueError("42 pattern overlaps entry or exit")
            self._change_wall(p_offset, "NESW", "close")
            self.maze[p_offset[1]][p_offset[0]] |= 0b11110000

    def _close(self, x: int, y: int, binary: int) -> None:
        """ closes the wall at the given coordinates
        by setting the corresponding bit in the maze grid

        Args:
            x (int): the x-coordinate of the cell to close the wall for
            y (int): the y-coordinate of the cell to close the wall for
            binary (int): the binary representation of the wall
            to close (1 for north, 2 for east, 4 for south, 8 for west)
        """
        self.maze[y][x] |= binary

    def _open(self, x: int, y: int, binary: int) -> None:
        """ opens the wall at the given coordinates

        Args:
            x (int): the x-coordinate of the cell to open the wall for
            y (int): the y-coordinate of the cell to open the wall for
            binary (int): the binary representation of the wall to open
        """
        self.maze[y][x] &= ~binary

    def _change_wall(self, p: tuple[int, int],
                     to_change: str, flag: str) -> None:
        """closes or opens the walls of a cell in the specified directions
        Args:
            point (tuple[int, int]): the coordinates of the cell
            to_change (str): a string containing the walls to modify
            flag (str): "close" to close the walls, "open" to open the walls
        """
        action: Callable[
            [int, int, int],
            None] = self._close if flag == "close" else self._open
        if 'N' in to_change:
            action(p[0], p[1], 0b0001)
            if p[1] > 0:
                action(p[0], p[1] - 1, 0b0100)
        if 'E' in to_change:
            action(p[0], p[1], 0b0010)
            if p[0] < self.width - 1:
                action(p[0] + 1, p[1], 0b1000)
        if 'S' in to_change:
            action(p[0], p[1], 0b0100)
            if p[1] < self.height - 1:
                action(p[0], p[1] + 1, 0b0001)
        if 'W' in to_change:
            action(p[0], p[1], 0b1000)
            if p[0] > 0:
                action(p[0] - 1, p[1], 0b0010)

    def reset_positions(self) -> None:
        self.maze[self.position[1]][self.position[0]] &= ~0b11000000
        self.maze[self.entry[1]][self.entry[0]] |= 0b10000000
        self.maze[self.exit[1]][self.exit[0]] |= 0b01000000
        self.position = self.entry

    def move_up(self) -> None:
        pos = self.position
        if not self.maze[pos[1]][pos[0]] & 0b0001:
            self.maze[pos[1]][pos[0]] &= ~0b11000000
            self.position = (pos[0], pos[1] - 1)

    def move_down(self) -> None:
        pos = self.position
        if not self.maze[pos[1]][pos[0]] & 0b0100:
            self.maze[pos[1]][pos[0]] &= ~0b11000000
            self.position = (pos[0], pos[1] + 1)

    def move_left(self) -> None:
        pos = self.position
        if not self.maze[pos[1]][pos[0]] & 0b1000:
            self.maze[pos[1]][pos[0]] &= ~0b11000000
            self.position = (pos[0] - 1, pos[1])

    def move_right(self) -> None:
        pos = self.position
        if not self.maze[pos[1]][pos[0]] & 0b0010:
            self.maze[pos[1]][pos[0]] &= ~0b11000000
            self.position = (pos[0] + 1, pos[1])

    def entry_exit(self) -> None:
        pos = self.position
        if pos == self.entry:
            self.maze[pos[1]][pos[0]] &= ~0b01000000
        elif pos == self.exit:
            self.maze[pos[1]][pos[0]] &= ~0b1000000

    def solve_maze(self,
                   with_animation: bool) -> Optional[Iterator[int]]:
        """
        Solves the maze using the A* algorithm.
        If with_animation is True, returns an iterator.
        If with_animation is False, runs to completion and returns None.
        """

        def _solve_generator() -> Iterator[int]:
            start = self.entry
            end = self.exit
            steps = 0

            def points_to_path(points: list[tuple[int, int]]) -> str:
                path = ""
                for i in range(len(points) - 1):
                    p1, p2 = points[i], points[i + 1]
                    if p1[0] == p2[0]:
                        path += "S" if p1[1] < p2[1] else "N"
                    else:
                        path += "E" if p1[0] < p2[0] else "W"
                return path

            def how_far(p: tuple[int, int]) -> int:
                return abs(p[0] - end[0]) + abs(p[1] - end[1])

            def get_neighbors(p: tuple[int, int]) -> list[tuple[int, int]]:
                neighbors = []
                if not self.maze[p[1]][p[0]] & 0b0001 and p[1] > 0:
                    neighbors.append((p[0], p[1] - 1))
                if (not self.maze[p[1]][p[0]] & 0b0010
                        and p[0] < self.width - 1):
                    neighbors.append((p[0] + 1, p[1]))
                if (not self.maze[p[1]][p[0]] & 0b0100
                        and p[1] < self.height - 1):
                    neighbors.append((p[0], p[1] + 1))
                if not self.maze[p[1]][p[0]] & 0b1000 and p[0] > 0:
                    neighbors.append((p[0] - 1, p[1]))
                return neighbors

            heap = [(how_far(start), 0, start, [start])]
            visited: set[tuple[int, int]] = set()

            while heap:
                _, cost, point, path = heappop(heap)

                if point == end:
                    for p in path:
                        self.maze[p[1]][p[0]] |= 0b11000000
                        if with_animation:
                            sys.stdout.write("\033[H\033[J")
                            time.sleep(0.04)
                            yield steps
                    self.maze[start[1]][start[0]] &= ~0b01000000
                    self.maze[end[1]][end[0]] &= ~0b10000000
                    for p in visited:
                        self.maze[p[1]][p[0]] &= ~0b10000
                    self.solution = points_to_path(path)
                    return
                if point in visited:
                    continue
                visited.add(point)
                steps += 1
                self.maze[point[1]][point[0]] |= 0b10000
                for neighbor in get_neighbors(point):
                    if neighbor not in visited:
                        new_cost = cost + 1
                        heappush(heap, (
                            new_cost + how_far(neighbor),
                            new_cost,
                            neighbor,
                            path + [neighbor]
                        ))
                if with_animation:
                    sys.stdout.write("\033[H\033[J")
                    time.sleep(0.04)
                    yield steps
        solver = _solve_generator()
        if with_animation:
            return solver
        else:
            for _ in solver:
                pass
            return None
