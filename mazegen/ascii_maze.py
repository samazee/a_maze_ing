import tomllib
from typing import Generator
import os
import sys
import termios
import tty
from .maze_generator import MazeGenerator


def load_colors(theme: str) -> dict[str, str]:
    """ loads a color scheme from the palettes folder, the color scheme is a

    Args:
        theme (str): the name of the color scheme to load,
        it should correspond to a .toml file

    Returns:
        dict[str, str]: a dictionary mapping color names
        to ANSI escape codes for background color
    """
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "palettes", f"{theme}.toml")
    with open(path, "rb") as f:
        _data = tomllib.load(f)

    def to_ansi(hex_color: str) -> str:
        """ converts a hex color code to an ANSI
        escape code for background color

        Args:
            hex_color (str): a hex color code in the format "#RRGGBB"

        Returns:
            str: an ANSI escape code for background color
            in the format "\033[48;2;R;G;Bm"
        """
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"\033[48;2;{r};{g};{b}m"

    colors = {k: to_ansi(v) for k, v in _data["maze_colors"].items()}
    colors["reset"] = "\033[0m"
    return colors


def color_generator() -> Generator[dict[str, str], None, None]:
    """ a generator that yields a color scheme from the palettes folder,

    Yields:
        Generator[dict[str, str], None, None]: a generator that yields a
        color scheme from the palettes folder
    """
    colors = [load_colors(theme) for theme in
              ["orange", "green", "red",
               "purple", "brown", "blue"]]
    while True:
        for color in colors:
            yield color


class AsciiMaze:
    def __init__(self, generator: MazeGenerator):
        """ a class representing an ASCII maze,
        it can render the maze to the console

        Args:
            maze (list[list[int]]): a 2D list of integers
            representing the maze, where each integer is a hex digit
        """
        self.generator: MazeGenerator = generator
        self.width = generator.width
        self.height = generator.height
        self.clr_gen = color_generator()
        self.clr = load_colors("blue")
        self.showpath = False

    def delete_path(self) -> None:
        """deletes the path from the maze, this is used to animate the solution
        """
        for r in range(self.height):
            for c in range(self.width):
                if (self.generator.maze[r][c] >> 4) == 0b1100:
                    self.generator.maze[r][c] &= 0b111111

    def next_color(self) -> None:
        """switches to the next color scheme
        """
        self.clr = next(self.clr_gen)

    def toggle_path(self) -> None:
        """toggles the visibility of the path in the maze
        """
        self.showpath = not self.showpath

    def draw(self) -> None:
        """renders the maze to the console

        Raises:
            ValueError: if no maze is provided
            and no maze is stored in the object
        """
        if self.generator.maze is None:
            raise ValueError("No maze to render")

        write = sys.stdout.write
        buff = []

        ROAD = self.clr["road"] + "  "
        WALL = self.clr["wall"] + "  "
        CELL = self.clr["cell"] + "    "
        BLOCK = self.clr["block"] + "  "
        SHADOW = self.clr["shadow"] + "  "
        VISITED = self.clr["visited"] + "    "
        CONNECTED = self.clr["connected"] + "    "
        ENTRY = self.clr["entry"] + "    "
        EXIT = self.clr["exit"] + "    "
        PATH = self.clr["path"] + "    " if self.showpath else CELL
        R = self.clr["reset"]
        M = BLOCK * 4
        NL = R + "\n"

        UPSHADOW = M + SHADOW * (self.width * 3 + 3) + M

        buff.append(f"{M + BLOCK * (self.width * 3 + 3) + M + NL}" * 2)
        buff.append(f"{UPSHADOW + NL}" * 2)

        line = M + SHADOW
        for point in self.generator.maze[0]:
            line += WALL
            if (point & 0b0001):
                line += WALL * 2
            else:
                line += ROAD * 2
        line += WALL + SHADOW + M + NL
        buff.append(line)

        for row in self.generator.maze:
            for _ in range(2):
                line = M + SHADOW
                if row[0] & 0b1000:
                    line += WALL
                else:
                    line += ROAD

                for point in row:
                    if ((point >> 4) == 0b1111):
                        line += BLOCK * 2
                    elif (point >> 6) == 0b11:
                        line += PATH
                    elif point & 0b10000000:
                        line += ENTRY
                    elif point & 0b1000000:
                        line += EXIT
                    elif point & 0b100000:
                        line += CONNECTED
                    elif (point & 0b10000):
                        line += VISITED
                    else:
                        line += CELL
                    if point & 0b0010:
                        line += WALL
                    else:
                        line += ROAD

                line += SHADOW + M + NL
                buff.append(line)

            line = M + SHADOW + WALL
            for point in row:
                if point & 0b0100:
                    line += WALL * 2
                else:
                    line += ROAD * 2
                line += WALL
            line += SHADOW + M + NL
            buff.append(line)

        buff.append(f"{M + BLOCK * (self.width * 3 + 3) + M + NL}" * 4)
        buff.append(f"{SHADOW * (self.width * 3 + 11) + NL}" * 2)

        write(''.join(buff))

    @staticmethod
    def read_key() -> str:
        """reads a single character from the user input without blocking
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        except Exception as e:
            print(f"\033[31mError reading input:\033[0m {e}")
            ch = ""
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch.lower()

    @staticmethod
    def display_menu(colors: dict[str, str]) -> None:
        """ displays the menu for controls and their descriptions

        Args:
            color (dict[str, str}): the colors to use for the menu display
        """
        beff = "\033[1m"
        teff = "\033[3m"

        bclr = colors["block"] + "\033[38;2;255;255;255m"
        rst = colors["reset"]

        print()
        print(
            f"{bclr}{beff} R {rst}|{bclr}{teff} Re-generate {rst}  "
            f"{bclr}{beff} C {rst}|{bclr}{teff} Change Color {rst}  "
            f"{bclr}{beff} S {rst}|{bclr}{teff} Solve {rst}  "
            f"{bclr}{beff} A {rst}|{bclr}{teff} Animate Solution {rst}  "
            f"{bclr}{beff} Q {rst}|{bclr}{teff} Quit {rst}  "
            f"{bclr}{beff} M {rst}|{bclr}{teff} Move {rst}  "
            f"{bclr}{beff} H {rst}|{bclr}{teff} Show/Hide Path {rst}  "
            f"{bclr}{beff} W {rst}|{bclr}{teff} Write to File {rst}"
            )

    @staticmethod
    def display_move_menu(colors: dict[str, str]) -> None:
        """ displays the menu for the free move mode,
        showing the controls and their descriptions

        Args:
            color (dict[str, str}): the colors to use for the menu display
        """
        beff = "\033[1m"
        teff = "\033[3m"

        bclr = colors["block"] + "\033[38;2;255;255;255m"
        rst = colors["reset"]

        print()
        print(
            f"{bclr}{beff} W {rst}|{bclr}{teff} Move Up {rst}  "
            f"{bclr}{beff} A {rst}|{bclr}{teff} Move Left {rst}  "
            f"{bclr}{beff} S {rst}|{bclr}{teff} Move Down {rst}  "
            f"{bclr}{beff} D {rst}|{bclr}{teff} Move Right {rst}  "
            f"{bclr}{beff} Q {rst}|{bclr}{teff} Quit {rst}  "
            )

    def render(self) -> None:
        self.generator.initialize()
        self.generator.wilson_algo()
        os.system('cls' if os.name == 'nt' else 'clear')
        sys.stdout.write("\033[H\033[J")
        self.draw()
        AsciiMaze.display_menu(self.clr)
        while True:
            key = AsciiMaze.read_key().lower()
            if key == "q":
                break
            elif key == "r":
                self.generator.initialize()
                self.generator.wilson_algo()
                os.system('cls' if os.name == 'nt' else 'clear')
                self.draw()
                AsciiMaze.display_menu(self.clr)
            elif key == "c":
                self.next_color()
                os.system('cls' if os.name == 'nt' else 'clear')
                self.draw()
                AsciiMaze.display_menu(self.clr)
            elif key == "s":
                self.generator.solve_maze(False)
                self.showpath = True
                os.system('cls' if os.name == 'nt' else 'clear')
                self.draw()
                AsciiMaze.display_menu(self.clr)
            elif key == "a":
                self.delete_path()
                self.showpath = True
                animator = self.generator.solve_maze(True)
                while (next(animator, None)  # type: ignore[arg-type]
                       is not None):
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self.draw()
                    AsciiMaze.display_menu(self.clr)
            elif key == "h":
                self.toggle_path()
                os.system('cls' if os.name == 'nt' else 'clear')
                self.draw()
                AsciiMaze.display_menu(self.clr)
            elif key == "m":
                self.showpath = True
                self.delete_path()
                pos = self.generator.position
                self.generator.maze[pos[1]][pos[0]] |= 0b11000000
                os.system('cls' if os.name == 'nt' else 'clear')
                self.draw()
                AsciiMaze.display_move_menu(self.clr)
                while True:
                    key = AsciiMaze.read_key().lower()
                    pos = self.generator.position
                    if pos == self.generator.exit:
                        break
                    if (key in ('q', '\x03', 'm')
                            or pos == self.generator.exit):
                        self.showpath = False
                        self.generator.reset_positions()
                        os.system('cls' if os.name == 'nt' else 'clear')
                        self.draw()
                        AsciiMaze.display_menu(self.clr)
                        break
                    elif key == 'w':
                        self.generator.move_up()
                    elif key == 'a':
                        self.generator.move_left()
                    elif key == 's':
                        self.generator.move_down()
                    elif key == 'd':
                        self.generator.move_right()
                    self.generator.entry_exit()
                    pos = self.generator.position
                    self.generator.maze[pos[1]][pos[0]] |= 0b11000000
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self.draw()
                    AsciiMaze.display_move_menu(self.clr)
            elif key == "w":
                try:
                    self.generator.write_to_file(self.generator.output_file)
                    print("\033[32mMaze written to "
                          f"{self.generator.output_file}\033[0m")
                except Exception as e:
                    print(f"\033[31mError writing to file:\033[0m {e}")
