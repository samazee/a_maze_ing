from typing import TextIO, Any
import os
import sys
from pydantic import BaseModel, Field, field_validator, ConfigDict
os.environ['PYDANTIC_ERRORS_INCLUDE_URL'] = '0'


class MazeConfig(BaseModel):
    """A class representing the configuration for a maze generator.

    Args:
        BaseModel (_type_): the base class for the MazeConfig,
        used for validation and parsing

    Raises:
        ValueError: if the config values are invalid
    """
    model_config = ConfigDict(hide_input_in_errors=True)
    width: int = Field(ge=9)
    height: int = Field(ge=7)
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None

    @field_validator('output_file')
    def validate_output_file(cls, v: str) -> str:
        """validate that the output file is a valid path

        Args:
            v (str): the output file path to validate

        Raises:
            ValueError: if the output file path is invalid

        Returns:
            str: the output file path if valid
        """
        if not v:
            raise ValueError("Output file cannot be empty")
        if os.path.isdir(v):
            raise ValueError(f"Output file '{v}' cannot be a directory")
        if v.endswith('.py'):
            raise ValueError("Output file cannot have a .py extension")
        return v

    @field_validator('entry', 'exit', mode='before')
    def validate_coordinates(cls, v: str) -> tuple[int, int]:
        """validate that the coordinates are in the correct format (x,y)

        Args:
            v (str): the coordinates to validate

        Raises:
            ValueError: if the coordinates are not in the correct format

        Returns:
            tuple[int, int]: the coordinates if valid
        """
        try:
            splitted = v.split(',')
            if len(splitted) != 2:
                raise ValueError("Config Error: must be in x,y format")
            return (int(splitted[0].strip()), int(splitted[1].strip()))
        except (ValueError, IndexError):
            raise ValueError("Config Error: coordinates must be in x,y format")

    @field_validator('entry', 'exit')
    def validate_bounds(cls, v: tuple[int, int], info: Any) -> tuple[int, int]:
        """validate that the coordinates are within the bounds of the maze

        Args:
            v (tuple[int, int]): the coordinates to validate

        Raises:
            ValueError: if the coordinates are out of bounds

        Returns:
            tuple[int, int]: the coordinates if valid
        """
        if info.data.get('width') and info.data.get('height'):
            x, y = v
            w = info.data['width']
            h = info.data['height']
            if not (0 <= x < w and 0 <= y < h):
                raise ValueError(f"Config Error: coordinates {v} out of bounds [{w}x{h}]")
        return v

    @field_validator('exit')
    def validate_is_same_points(cls, v: tuple[int, int],
                            info: Any) -> tuple[int, int]:
        """validate that entry and exit are not the same point

        Args:
            v (tuple[int, int]): the exit coordinates

        Raises:
            ValueError: if the entry and exit are the same point

        Returns:
            tuple[int, int]: the exit coordinates if valid
        """
        if info.data.get('entry') and v == info.data['entry']:
            raise ValueError("Config Error: entry and exit must be different")
        return v

    @classmethod
    def from_file(cls, fl: TextIO) -> 'MazeConfig':
        """initiates a MazeConfig from a config file

        The config file should be in the following format:
            WIDTH=32
            HEIGHT=24
            ENTRY=0,0
            EXIT=27,19
            OUTPUT_FILE=maze.txt
            PERFECT=True
            SEED=12345 (optional)

        Args:
            filename (TextIO): the config file to read from

        Raises:
            ValueError: if the config file is invalid or missing required keys

        Returns:
            MazeConfig: the MazeConfig object created from the config file
        """
        required = [
            "WIDTH", "HEIGHT", "ENTRY",
            "EXIT", "OUTPUT_FILE", "PERFECT"
            ]
        try:
            data: dict[str, str] = {}
            for line in fl:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, _, value = line.partition("=")
                k = key.strip().upper()
                v = value.strip().upper()
                if k in data and k in required and v != data[k]:
                    raise ValueError(f"Config Error: duplicate key: {key.strip()}")
                data[key.strip().upper()] = value.strip()
        except FileNotFoundError:
            raise ValueError(f"Config Error: config file '{fl.name}' not found.")
        except PermissionError:
            raise ValueError(f"Config Error: permission denied for config file '{fl.name}'.")
        except OSError as e:
            raise ValueError(f"Config Error: error opening config file '{fl.name}': {e}")
        except Exception as e:
            raise ValueError(f"Config Error: error reading config file: {e}")
        missing = [k for k in required if k not in data]
        if missing:
            raise ValueError(f"Config Error: missing required keys: {', '.join(missing)}")

        try:
            return cls(
                width=int(data["WIDTH"]),
                height=int(data["HEIGHT"]),
                entry=data["ENTRY"],  # type: ignore
                exit=data["EXIT"],  # type: ignore
                output_file=data["OUTPUT_FILE"],
                perfect=data["PERFECT"].lower() in ("true", "1", "yes"),
                seed=int(data["SEED"]) if "SEED" in data
                else None,
            )
        except ValueError as e:
            raise ValueError(f"Config Error: invalid config values: {e}")


    @staticmethod
    def new() -> 'MazeConfig':
        try:
            with open(sys.argv[1]) as f:
                return MazeConfig.from_file(f)
        except Exception as e:
            raise e 


    def get_config(self) -> dict[str, Any]:
        """return the config as a dict, useful for printing and debugging.

        Returns:
            dict: the config as a dict
        """
        return {
            "width": self.width,
            "height": self.height,
            "entry": self.entry,
            "exit": self.exit,
            "output_file": self.output_file,
            "perfect": self.perfect,
            "seed": self.seed
        }
