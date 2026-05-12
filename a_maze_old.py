import sys
import termios
import tty
try:
    from pydantic import ValidationError
    from mazegen import MazeGenerator, AsciiMaze, MazeConfig
except ImportError as e:
    print(f"\033[31mMissing dependency:\033[0m {e}")
    print("Run: make install")
    sys.exit(1)


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


def display_menu(colors: dict[str, str]) -> None:
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


def render(mzgen: MazeGenerator, mzcnf: MazeConfig, mzasci: AsciiMaze) -> None:
    while True:
        sys.stdout.write("\033[H\033[J")
        mzasci.draw(mzgen.maze)
        display_menu(mzasci.clr)
        key = read_key().lower()
        if key == "q":
            break
        elif key == "r":
            mzgen.initialize()
            mzgen.wilson_algo()
            mzasci = AsciiMaze(mzgen.maze)
            mzgen.connect_ascii(mzasci)
        elif key == "c":
            mzasci.next_color()
        elif key == "s":
            mzgen.solve_maze(False)
            mzasci.showpath = True
        elif key == "a":
            mzasci.delete_path()
            mzasci.showpath = True
            mzgen.solve_maze(True)
        elif key == "h":
            mzasci.toggle_path()
        elif key == "m":
            mzasci.showpath = True
            mzasci.delete_path()
            mzgen.free_move()
        elif key == "w":
            try:
                mzgen.write_to_file(mzcnf.output_file)
                print(f"\033[32mMaze written to {mzcnf.output_file}\033[0m")
            except Exception as e:
                print(f"\033[31mError writing to file:\033[0m {e}")


def start_maze_interaction() -> None:
    """the main function of the program,
    it initializes the maze generator,
    the ascii maze and starts the interactive menu
    """
    try:
        mzcnf = MazeConfig.new()
    except (ValueError, ValidationError) as e:
        raise ValueError(f"\033[31mConfig Error:\033[0m {e}")

    try:
        mzgen = MazeGenerator.new(mzcnf)
        mzgen.initialize()
    except ValueError as e:
        raise ValueError(f"\033[31mMaze Generation Error:\033[0m {e}")

    mzasci = AsciiMaze(mzgen.maze)

    try:
        mzgen.wilson_algo()
        mzgen.solve_maze(False)
    except Exception as e:
        raise ValueError(f"\033[31mMaze Generation Error:\033[0m {e}")

    try:
        render(mzgen, mzcnf, mzasci)
    except Exception as e:
        raise ValueError(f"\033[31mInteraction Error:\033[0m {e}")


if __name__ == "__main__":
    try:
        start_maze_interaction()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        raise e
        sys.exit(1)
