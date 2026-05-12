## *This project has been created as part of the 42 curriculum by aait-idi, azgor.*

<!-- 9sem -->
<div style="display: flex; justify-content: space-between; align-items: center;">
  <span style="font-size: 45px;">📄</span>
  <span style="font-size: 40px;">&lt;/&gt;</span>
  <span style="font-size: 40px;">🐪</span>
</div>

![Banner](assets/banner.png)

# Description
The goal of this project is to create a maze generator and solver. The program will generate a maze based on a given configuration file and then solve it using a chosen algorithm. The maze will be displayed in the terminal, and the solution will be highlighted.

<!-- Instructions -->
# Instructions
Our program runs with the following command:

```sh
python3 a_maze_ing.py config.txt
```
- `a_maze_ing.py` is our main program file.

- `config.txt` is our config file where we can insert the following :

To install the project requiremenets, run the following command in the terminal:

```Make
make install  # uses python3.11
```

To run the program, use the following command:

```Make
make run
```

To clean the project, use the following command:

```Make
make clean # deletes: __pycache__, */__pycache__, .mypy_cache
```

To lint the code, use the following command:

```Make
make lint # uses flake8 & mypy
```

# Resources
- [Maze Generation Algorithms](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- AI was used to assist in the development of this projects's repetetive and tedious tasks, as well as to optimize the code for better performance. AI tools were also utilized for code review and debugging purposes.


# Additionals

## Config file structure
The configuration file is a simple text file that contains the following parameters:

```
WIDTH=20 -> the width of the maze
HEIGHT=10 -> the height of the maze
ENTRY=1,1 -> the coordinates of the maze entry point (x,y)
EXIT=18,8 -> the coordinates of the maze exit point (x,y)
OUTPUT_FILE=maze.txt -> the name of the file where the generated maze will be saved
PERFECT=True -> whether the maze should be perfect (no loops) or not
SEED=12345 (optional) -> the seed for the random number generator, which can be used to generate the same maze multiple times for testing purposes
```

## Maze generation algorithm
The maze generation algorithm used in this project is Wilson's algorithm. This algorithm is based on the concept of random walks and is known for producing perfect mazes (mazes without loops).

## Why Wilson's algorithm
Wilson's algorithm was chosen for this project because it is efficient and produces high-quality mazes. It is also relatively easy to implement and understand, making it a suitable choice for this project.

## Reusable code
The code for the maze generation and solving algorithms can be reused in other projects that require similar functionality. The code is modular and can be easily integrated into other applications.

## Team and project management
- Team members: aait-idi (Maze Generation, Path finding, ...), yoabied (parsing, config validation and program stracture)
- Anticipated planning: The project was planned to be completed in 2 weeks, with each week dedicated to a specific phase of the project (planning, implementation, testing, and documentation). The planning changes as we progressed through the project.
- What worked well: We was able to effectively communicate and collaborate throughout the project, which helped to ensure that tasks were completed on time and to a high standard.
- What could be improved: We could have spent more time refining the project and mazegeneration implimentation, as well as testing the code more thoroughly to identify and fix any bugs or issues.
- Tools used: We used Git for version control, and a code editor Visual Studio Code for writing and editing the code. We also utilized AI tools for code review and debugging purposes.

-----------

<div style="display: flex; justify-content: space-between; align-items: center;">
  <span style="font-size: 45px;">📄</span>
  <span style="font-size: 40px;">&lt;/&gt;</span>
  <span style="font-size: 40px;">🐪</span>
</div>

-----------
