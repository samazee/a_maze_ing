from mazegen import MazeGenerator, MazeConfig, AsciiMaze
import sys

if __name__ == '__main__':
    try:
        argc = len(sys.argv)
        if argc != 2:
            raise ValueError("Usage: python a_maze_ing.py <config_file>")
        conf = MazeConfig.new()
        gen = MazeGenerator.new(conf)
        display = AsciiMaze(gen)
        display.render()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
