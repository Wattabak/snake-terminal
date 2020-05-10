import curses
import logging
from curses import textpad
from typing import Tuple, List, Sequence
from models import Snake, Direction, Terrain

logging.basicConfig(filename='snake.log', level=logging.DEBUG)


def draw_ch_list(window,
                 coordinates: List[Tuple[int, int]],
                 ch_list: Sequence[str]) -> None:
    for i, (y, x) in enumerate(coordinates):
        draw_ch(window, y=y, x=x, ch=ch_list[i])
    window.refresh()


def draw_ch(window, y: int, x: int, ch: str):
    window.addstr(y, x, ch)  # put new


def run(window) -> None:
    curses.curs_set(0)

    # Create playable area
    max_height, max_width = window.getmaxyx()

    padding = [4, 4, 4, 4]  # top, right, bottom, left

    height = max_height - padding[0] - padding[2]
    width = max_width - padding[1] - padding[3]
    logging.info(f"Window drawn: height: {height} \n width: {width}")

    win_left_corner, win_right_corner = ([padding[0], padding[3]],
                                         [max_height - padding[2], max_width - padding[1]])
    terrain = Terrain(width=width, height=height)
    # draw playable area
    textpad.rectangle(
        window,
        win_left_corner[0],
        win_left_corner[1],
        win_right_corner[0],
        win_right_corner[1],
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

    # run a game
    while True:
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
        else:
            continue
        cur_tail_y, cur_tail_x = snake.current_coordinates[-1]

        draw_ch(window,
                y=cur_tail_y,
                x=cur_tail_x,
                ch=" "
                )  # erase previous tail

        snake.move(direction=direction)  # create new coordinates

        draw_ch_list(window,
                     coordinates=snake.current_coordinates,
                     ch_list=snake.body
                     )  # draw new coords


if __name__ == '__main__':
    curses.wrapper(run)
