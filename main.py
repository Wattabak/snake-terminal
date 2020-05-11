import curses
import logging
from curses import textpad
from typing import Tuple, List, Sequence

from models import Snake, Direction, Terrain, SnakeBorderHit, SnakeOuroboros

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
    window.clear()
    curses.curs_set(0)

    # Create playable area
    max_height, max_width = window.getmaxyx()

    padding = [4, 4, 4, 4]  # top, right, bottom, left

    height = max_height - padding[0] - padding[2]
    width = max_width - padding[1] - padding[3]
    logging.info(f"Window sizes: height: {height} \n width: {width}")

    win_left_corner, win_right_corner = ([padding[0], padding[3]],
                                         [max_height - padding[2], max_width - padding[1]])
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
        try:
            snake.move(direction=direction)  # create new coordinates
        except Exception as e:
            game_over(window, center, e)

        draw_ch_list(window,
                     coordinates=snake.current_coordinates,
                     ch_list=snake.body
                     )  # draw new coords


def game_over(window, center, ending: Exception, score: int=0, time_elapsed= None):
    window.clear()
    logging.info(ending)
    if isinstance(ending, SnakeBorderHit):
        ending = "You hit a wall!"
    if isinstance(ending, SnakeOuroboros):
        ending = "You ate yourself?!"
    window.addstr(*center, f"GAME OVER, {ending}")
    window.addstr(center[0]+1, center[1], f"Your score: {score}")
    window.addstr(center[0]+4, center[1], "Try again?[y]/[n]")
    window.keypad(1)
    key = window.getch()
    if key == ord("y"):
        run(window)
    if key == ord("n") or key == 3:
        raise KeyboardInterrupt
    else:
        game_over(window, center, score, time_elapsed)

if __name__ == '__main__':
    curses.wrapper(run)
