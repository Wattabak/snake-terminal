import curses
import logging
import random
from curses import textpad
from typing import Tuple, List, Sequence

from models import Snake, Direction, Terrain, SnakeBorderHit, SnakeOuroboros

logging.basicConfig(filename='snake.log', level=logging.DEBUG)

base_settings = {
    "borders": None,
    "board_height": 10,
    "board_width": 10,
}

prod_settings = {
    "borders": ["left", "right", "top", "bottom"],
    "board_height": 10,
    "board_width": 10,
}


def draw_ch_list(window,
                 coordinates: List[Tuple[int, int]],
                 ch_list: Sequence[str]) -> None:
    for i, (y, x) in enumerate(coordinates):
        draw_ch(window, y=y, x=x, ch=ch_list[i])
    window.refresh()


def draw_ch(window, y: int, x: int, ch: str):
    window.addch(y, x, ch)  # put new


def get_food_coords(snake: Snake,
                    terrain: Terrain) -> Tuple[int, int]:
    food_y, food_x = (
        random.randint(terrain.min_height + 1, terrain.max_height - 1),
        random.randint(terrain.min_width + 1, terrain.max_width - 1)
    )
    if (food_y, food_x) in snake.current_coordinates:
        food_y, food_x = get_food_coords(snake, terrain)
    return food_y, food_x


def run(window) -> None:
    window.clear()
    curses.curs_set(0)

    # Create playable area
    max_height, max_width = window.getmaxyx()

    padding = [4, 4, 4, 4]  # top, right, bottom, left

    # height = max_height - padding[0] - padding[2]
    # width = max_width - padding[1] - padding[3]
    height = max_height - padding[0] - padding[2]
    width = 20
    logging.info(f"Window sizes: height: {height} \n width: {width}")

    win_left_corner, win_right_corner = ([padding[0], padding[3]],
                                         [padding[0] + height, padding[1] + width])
    terrain = Terrain(width=width,
                      height=height,
                      max_height=win_right_corner[0],
                      min_height=win_left_corner[0],
                      min_width=win_left_corner[1],
                      max_width=win_right_corner[1],
                      borders=[Direction.UP]
                      )
    # draw playable area
    textpad.rectangle(
        window,
        *win_left_corner,
        *win_right_corner,

    )
    center = win_left_corner[0] + height // 2, win_right_corner[1] // 2

    # Create a snake
    snake_body = 4
    snake_coordinates = [center]
    index = 0
    while len(snake_coordinates) != snake_body:
        prev = snake_coordinates[index]
        snake_coordinates.append((prev[0], prev[1] - 1))
        index += 1
    logging.info(snake_coordinates)
    snake = Snake(initial_coordinates=snake_coordinates, body_length=snake_body, terrain=terrain)

    # Draw a snake
    draw_ch_list(window,
                 coordinates=snake.initial_coordinates,
                 ch_list=snake.body
                 )
    # Create and draw food
    food = curses.ACS_PI
    food_y, food_x = get_food_coords(snake, terrain)
    window.addch(food_y, food_x, food)
    # run a game
    direction = Direction.RIGHT

    score = 0
    # draw score
    window.addstr(1, 1, f"Score: {score}")
    while True:
        window.timeout(100)
        key = window.getch()
        movement = {
            curses.KEY_UP: Direction.UP,
            curses.KEY_DOWN: Direction.DOWN,
            curses.KEY_LEFT: Direction.LEFT,
            curses.KEY_RIGHT: Direction.RIGHT
        }
        new_direction = movement.get(key)
        if new_direction:
            direction = new_direction
            logging.info(f"Change directions key caught: \n key - {key} \n direction - {direction}")
            logging.info(snake.current_coordinates)

        elif key == 3:
            raise KeyboardInterrupt
        cur_tail_y, cur_tail_x = snake.current_coordinates[-1]

        try:
            snake.move(direction=direction)  # create new coordinates
        except Exception as e:
            logging.exception(f"Exception: {e}")
            window.timeout(0)
            game_over(window, center, e, score)
        draw_ch(window,
                y=cur_tail_y,
                x=cur_tail_x,
                ch=" "
                )  # erase previous tail

        draw_ch_list(window,
                     coordinates=snake.current_coordinates,
                     ch_list=snake.body
                     )  # draw new coords

        if snake.current_coordinates[0] == (food_y, food_x):
            score += 1
            snake.grow()
            food_y, food_x = get_food_coords(snake, terrain)
            window.addch(food_y, food_x, food)
        window.addstr(1, 1, f"Score: {score}")


def game_over(window,
              center,
              ending: Exception,
              score: int = 0,
              time_elapsed=None):
    window.clear()
    logging.info(ending)
    if isinstance(ending, SnakeBorderHit):
        ending = "You hit a wall!"
    if isinstance(ending, SnakeOuroboros):
        ending = "You ate yourself?!"
    while True:
        window.addstr(*center, f"GAME OVER, {ending}")
        window.addstr(center[0] + 1, center[1], f"Your score: {score}")
        window.addstr(center[0] + 4, center[1], "Try again?[y]/[n]")
        window.keypad(1)
        key = window.getch()
        if key == ord("y"):
            run(window)
        if key == ord("n") or key == 3:
            raise KeyboardInterrupt


if __name__ == '__main__':
    try:
        curses.wrapper(run)
    except KeyboardInterrupt:
        print("Thanks for playing!")
