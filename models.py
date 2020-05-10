import enum
from typing import List, Tuple, Optional


class Direction(enum.Enum):
    UP = 1
    DOWN = -1
    LEFT = 2
    RIGHT = -2


class Terrain:

    def __init__(self,
                 height: int,
                 width: int,
                 borders: Optional[List[Direction]] = None):
        self.height = height
        self.width = width

        self.area = self.height * self.width
        self.borders = borders  # without borders reaching the max constraint it will teleport the snake


class Snake:

    def __init__(self,
                 initial_coordinates: List[Tuple[int, int]],
                 terrain: Terrain,
                 body_length: int = 3,
                 ):
        self.initial_coordinates = initial_coordinates  # 0 - head
        self.current_coordinates = self.initial_coordinates  # tracks current coordinates

        self.terrain = terrain

        self.body_length = body_length
        self.direction = Direction.RIGHT

    @property
    def body(self):
        return u"\u25AF" * self.body_length

    @property
    def length(self) -> int:
        return len(self.body)

    @property
    def head(self) -> Tuple[int, int]:
        return self.current_coordinates[0]

    def move(self,
             direction: Direction) -> None:
        if not isinstance(direction, Direction):
            return
        # if direction == -self.direction:
        #     # for now just dont move at all if the opposite direction was issued
        #     return
        self.direction = direction

        how_much = 1
        movement = {
            Direction.UP: (0, -how_much),
            Direction.DOWN: (0, how_much),
            Direction.LEFT: (-how_much, 0),
            Direction.RIGHT: (how_much, 0)
        }
        change_x, change_y = movement[direction]

        head_y, head_x = self.current_coordinates[0][0], self.current_coordinates[0][1]
        new_head = (head_y + change_y, head_x + change_x)

        if 0 < new_head[0] < self.terrain.height:
            self.current_coordinates.insert(0, new_head)
        del self.current_coordinates[-1]
