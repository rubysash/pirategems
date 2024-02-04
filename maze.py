import base64
import io
import random
import sys
import textwrap
import time
from collections import deque

import pygame
import pygame.mixer

import assets
from generate import (recursive_backtracking, set_crystals, set_exit,
                      set_monsters)
from player_movement import move_player
from variables import *

'''
AI created "maze" game, with quite a bit of steering!
You are greybeard, searching for your gems that you stashed
away in caves that are now infested with toxic goblins
If they touch you, you die instantly.
If you kill them, the poison the air a bit more.
Every step you take poisons you a little.
You get the will to keep going  when you find another gem, or an exit.
Play until your greed kills you, or you "escape" with your gems.



# CLEANUP UNUSED CODE
vulture maze.py

# VARIOUS CODE RECOMMENDATIONS
python -m pip install flake8
flake8 --benchmark --color always --ignore=E501,F405 maze.v18b.py
pylint maze.v18b.py --disable=invalid-name,W0621,C0301,E1101

# REWRITES CODE TO PEP8 FORCEFULLY
python -m pip install black
black maze.py

# IS CODE USED?
python -m pip install coverage
coverage run -m unittest your_tests.py
python -m pip install deadcode?
deadcode maze.py

# TOO COMPLEX? REFACTOR CANDIDATES
python -m pip install radon
radon cc|mi|hal mazy.py
A = good, D = Bad

# SECURITY
python -m pip install bandit
bandit -r path/to/code
python -m pip install safety
safety check

todo, group:
utility.py
    clear_screen
    timer_decorator

state.py
    check_end_conditions
    load_next_level
    post_movement_processing
    terminate_game
    exit_game

display.py
    display_message
    display_loading_screen
    handle_paused_game
    display_help_commands
    draw_messages
    draw_game_screen
    draw_maze_and_monsters

interactions.py
    check_for_crystal_collision
    check_for_exit_collision
    check_for_monster_collision
    find_closest_monster
    handle_crystal_collision
    handle_exit_collision
    handle_monster_collision
    handle_monster_death
    search_corpse
    shoot_bullet

calculations.py
    bresenham_line
    has_wall_between
    light_intensity
    move_monster
    move_monsters
    update_seen_flags
    update_visibility_arrays
    valid_move

audio.py
    play_random_ambient
    play_random_cough
    make_wav_from_base64
'''

print("v18 beta")


# Start pygame and the sound system
pygame.init()
pygame.mixer.init()

# font
font = pygame.font.SysFont(None, 40)

# sounds
# Set up the end event for the music
MUSIC_ENDED = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(MUSIC_ENDED)

screen = pygame.display.set_mode(size)
pygame.display.set_caption("AI - Mazing")
font = pygame.font.Font(None, 36)  # None uses the default font; 36 is the font size

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Define a queue for messages
message_queue = deque()
current_message = None
message_end_time = 0


def timer_decorator(func):
    """
    Decorator to time the duration of function execution.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The wrapped function which prints the execution time.
    """

    def wrapper(*args, **kwargs):
        """
        Wrapper function to calculate the execution time.

        Args:
            *args: Variable length argument list of the decorated function.
            **kwargs: Arbitrary keyword arguments of the decorated function.

        Returns:
            The result of the decorated function.
        """
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"{func.__name__} took {elapsed_time} seconds to run")
        return result

    return wrapper


def add_message(source, message_text, color, duration):
    """
    Add a new message to the message queue to be displayed later.

    Args:
        source (str): The origin/source of the message.
        message_text (str): The content of the message.
        color (tuple): RGB color tuple for the message.
        duration (int): The duration the message will be displayed for in milliseconds.
    """
    if not terminate_after_message:
        print(f"LOGGING (MESSAGE): {message_text}")
        message_queue.append({
            'text': message_text,
            'color': color,
            'duration': duration,
            'source': source
        })


def light_intensity(x, y, light_x, light_y, LIGHT_RANGE):
    """
    Calculate the light intensity based on the distance from the light source.

    Args:
        x (int): x-coordinate of the object.
        y (int): y-coordinate of the object.
        light_x (int): x-coordinate of the light source.
        light_y (int): y-coordinate of the light source.
        LIGHT_RANGE (float): The range of the light.

    Returns:
        float: The intensity of the light at the given (x, y) location.
    """
    distance = ((x - light_x) ** 2 + (y - light_y) ** 2) ** 0.5
    intensity = 255 * (1 - (distance / LIGHT_RANGE))
    return intensity


def check_for_monster_collision():
    """
    Check if the player collided with a live or dead monster. If so, handle the respective collision.
    """
    global dead_monsters

    # Check if player collided with a live monster
    if monsters[player_y][player_x] == 1:
        handle_monster_collision()

    # Check if player stepped on a dead monster
    if (player_x, player_y) in dead_monsters:
        search_corpse(gross_messages)

        # Remove the dead monster after it's been looted
        dead_monsters.remove((player_x, player_y))


def handle_monster_collision():
    """
    Handle the collision between the player and a live monster.
    """
    global score, game_ended

    goblin_sound.play()

    if game_ended:
        return

    add_message('handle_monster_collision',
                "Your Search for Treasure is Over. You were eaten!", RED, 5000)
    terminate_game("collision")


def terminate_game(reason=""):
    """
    Terminate the game based on the given reason.

    Args:
        reason (str): The reason for terminating the game.
                      It can be "points", "collision", or any other reason.
    """
    global crystal_value, terminate_after_message

    if total_crystals == 0:
        crystal_value = 0

    if reason == "points":
        add_message('main_loop',
                    f"Out of Air! {total_crystals} gems. Largest gem was {crystal_value}.",
                    GOLD, 5000)
    elif reason == "collision":
        add_message('main_loop',
                    f"Monster Collision! {total_crystals} gems. Largest gem was {crystal_value}.",
                    RED, 5000)
    else:
        add_message('main_loop',
                    f"Escaped with {total_crystals} gems. Largest gem was {crystal_value}",
                    GOLD, 5000)

    terminate_after_message = True


def check_for_crystal_collision(crystal_value):
    """
    Check if the player collided with a crystal. If so, handle the collision.

    Args:
        crystal_value (int): The value of the crystal.
    """
    global crystals

    if maze[player_y][player_x] == 2:
        handle_crystal_collision(player_y, player_x, crystal_value, found_gem)


def handle_crystal_collision(y, x, crystal_value, messages):
    """
    Handle the collision between the player and a crystal.

    Args:
        y (int): The y-coordinate of the player.
        x (int): The x-coordinate of the player.
        crystal_value (int): The value of the crystal.
        messages (list): List of possible messages to display upon crystal collection.
    """
    global score, total_crystals

    if maze[y][x] == 2:
        score += crystal_value
        maze[y][x] = 0
        add_message('handle_crystal_collection',
                    random.choice(messages), BLUE, 1500)
        total_crystals += 1
        crystals_sound.play()


def handle_paused_game():
    """
    Handle the game when it is in a paused state.
    The screen is cleared, the help commands are displayed, and the function checks for user input to
    resume or quit the game.
    """
    global paused

    while paused:
        screen.fill(BLACK)
        display_help_commands(screen, font, HELP_COMMANDS)
        pygame.display.flip()

        for pause_event in pygame.event.get():
            if pause_event.type == pygame.QUIT:
                paused = False

            elif pause_event.type == pygame.KEYDOWN:
                paused = False


def display_help_commands(screen, font, commands):
    """
    Display the game's help commands on the screen when paused.

    Args:
        screen (pygame.Surface): The screen to render the text on.
        font (pygame.Font): The font to use for rendering.
        commands (dict): Dictionary containing command descriptions and associated keys.
    """
    # Start with the title
    title_text = font.render("GAME IS PAUSED", True, BLUE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 15))
    screen.blit(title_text, title_rect)

    # Calculate starting y position for the description
    start_y = title_rect.bottom + 25

    # If there's a game description, render it first
    if "description" in commands:
        description = commands["description"]
        wrapped_description = textwrap.wrap(description, width=50)
        for line in wrapped_description:
            desc_text = font.render(line, True, WHITE)
            screen.blit(desc_text, (SCREEN_WIDTH // 10, start_y))
            start_y += font.get_height() + 5

        # Additional spacing between description and commands table
        start_y += 20

    # Render the commands
    for key, value in commands.items():
        if key == "description":
            continue  # Skip the description

        key_text = font.render(key, True, VIOLET)
        value_text = font.render(value, True, GOLD)

        # Position the key closer to the left
        key_pos = (SCREEN_WIDTH // 10, start_y)

        # Position the value to the right of the key, with some buffer for spacing
        buffer_space = 20
        value_pos = (key_pos[0] + key_text.get_width() + buffer_space, start_y)

        screen.blit(key_text, key_pos)
        screen.blit(value_text, value_pos)

        # Move to the next line
        start_y += font.get_height() + 10


def draw_messages():
    """
    Draw game messages on the screen. If a message is currently being displayed and its duration has
    expired, it gets removed. If no message is displayed, the next message from the queue is fetched.
    """
    global current_message, message_end_time

    # Check if there's a currently displayed message and if its duration has expired
    if current_message and pygame.time.get_ticks() > message_end_time:
        current_message = None

    # If no message is currently displayed, get the next message from the queue
    if not current_message and message_queue:
        current_message = message_queue.popleft()
        message_end_time = pygame.time.get_ticks() + current_message['duration']

    # Draw the current message
    if current_message:
        text_surface = font.render(current_message['text'], True, current_message['color'])
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        screen.blit(text_surface, text_rect)


def check_for_exit_collision(exit_value):
    """
    Check if the player has collided with the exit in the maze.

    Args:
        exit_value (int): The value associated with the exit.
    """
    if maze[player_y][player_x] == 3:
        print(f"FOUND EXIT! at {player_x}, {player_y}")
        handle_exit_collision(player_y, player_x, exit_value)


def handle_exit_collision(y, x, exit_value):
    """
    Handle the collision between the player and the exit.

    Args:
        y (int): The y-coordinate of the exit in the maze.
        x (int): The x-coordinate of the exit in the maze.
        exit_value (int): The value associated with the exit.
    """
    global score

    if maze[y][x] == 3:  # if exit
        maze[y][x] = 0  # make the spot empty after collecting
        score += exit_value
        add_message('handle_exit_collision', "You Go Deeper, Searching for Treasure", RED, 2000)
        load_next_level(x, y)


@timer_decorator
def load_next_level(start_x, start_y):
    '''
    Load and initialize the next level of the game.

    Args:
        start_x: Starting x-position for generating the maze.
        start_y: Starting y-position for generating the maze.
    '''
    global maze, monsters, visibility, monster_visibility, monster_density
    global target_monster, dead_monsters, monster_blink_state, crystal_blink_state
    global crystal_value, toxicity_value

    display_loading_screen(assets.BASE64_IMG_PIRATE)

    # Transition ambient sounds between levels
    pygame.mixer.music.fadeout(1000)  # Fade out the current sound over 1 second
    play_random_ambient()  # Play a new ambient track for the new level

    # Modify level-specific variables
    monster_density += 0.5
    crystal_value += 5
    toxicity_value -= 3

    print(f"STATUS: Monster Density: {monster_density}")

    # Regenerate game objects and layout for the new level
    maze = recursive_backtracking(ROWS, COLS, start_x, start_y)
    maze = set_exit(maze, start_x, start_y)
    monsters = set_monsters(maze, start_x, start_y, monster_density)
    maze = set_crystals(maze)

    # Reset visibility states
    visibility = [[False for _ in range(COLS)] for _ in range(ROWS)]
    monster_visibility = [[False for _ in range(COLS)] for _ in range(ROWS)]

    # Reset other game state variables
    target_monster = None
    dead_monsters = []
    monster_blink_state = False
    crystal_blink_state = True

    clear_screen()  # Refresh the game screen
    new_sound.play()  # Play sound for the new level


def update_visibility_arrays(light_x, light_y, LIGHT_RANGE, COLS, ROWS, visibility, monster_visibility):
    '''
    Update visibility and shade of monsters based on the light's distance.

    Args:
        light_x, light_y: Position of the light source.
        LIGHT_RANGE: Range of the light source.
        COLS, ROWS: Dimensions of the game board.
        visibility: Array representing visibility of cells.
        monster_visibility: Array representing visibility of monsters.

    Returns:
        Updated visibility and monster_visibility arrays.
    '''
    for x in range(light_x - LIGHT_RANGE, light_x + LIGHT_RANGE + 1):
        for y in range(light_y - LIGHT_RANGE, light_y + LIGHT_RANGE + 1):
            if 0 <= x < COLS and 0 <= y < ROWS and (x - light_x)**2 + (y - light_y)**2 <= LIGHT_RANGE**2:
                intensity = light_intensity(x, y, light_x, light_y, LIGHT_RANGE)
                visibility[y][x] = (intensity, intensity, 0)
                monster_visibility[y][x] = (intensity, 0, 0)

    return visibility, monster_visibility


def draw_game_screen(screen, player_x, player_y, light_x, light_y, maze, visibility, monsters, monster_visibility, SEEN, UNSEEN, target_monster, monster_blink_state, crystal_blink_state, mouse_x, mouse_y, score, font):
    '''
    Draws the game screen, including the maze, monsters, light, and player. Also displays the score.

    Args:
        Various game state parameters including screen, player's position, light's position, maze, visibility map, etc.

    Returns:
        None
    '''
    # Clear the screen
    screen.fill(BLACK)

    # Draw the maze, monsters, etc.
    draw_maze_and_monsters(screen, maze, light_x, light_y, visibility, monsters, monster_visibility, SEEN, UNSEEN, target_monster, monster_blink_state, crystal_blink_state)

    # Draw the player
    pygame.draw.circle(screen, PLAYER, (player_x * CELL_SIZE + CELL_SIZE // 2, player_y * CELL_SIZE + CELL_SIZE // 2), LIGHT_RANGE)

    # Draw the light
    pygame.draw.circle(screen, LIGHT, (light_x * CELL_SIZE + CELL_SIZE // 2, light_y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2)

    # Show x, y of mouse
    if mouse_x is not None and mouse_y is not None:
        cell_x = mouse_x // CELL_SIZE
        cell_y = mouse_y // CELL_SIZE
        coords_text = font.render(f"{cell_x}, {cell_y}", True, WHITE)
        coords_text_rect = coords_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))
        screen.blit(coords_text, coords_text_rect)

    # Show the player's score
    score_text = font.render(f"Score: {score}", True, WHITE)
    score_text_rect = score_text.get_rect(topleft=(10, 10))
    screen.blit(score_text, score_text_rect)

    pygame.display.flip()


def draw_maze_and_monsters(screen, maze, light_x, light_y, visibility, monsters, monster_visibility, SEEN, UNSEEN, target_monster, monster_blink_state, crystal_blink_state):
    '''
    Draws the maze's walls, monsters, crystals, and exit based on current visibility and game state.

    Args:
        Various parameters for game state like the screen, maze structure, monster and crystal states, etc.

    Returns:
        None
    '''
    for y in range(len(maze)):
        for x in range(len(maze[y])):
            distance = ((x * CELL_SIZE + CELL_SIZE // 2) - (light_x * CELL_SIZE + CELL_SIZE // 2)) ** 2 + ((y * CELL_SIZE + CELL_SIZE // 2) - (light_y * CELL_SIZE + CELL_SIZE // 2)) ** 2

            # Determine base visibility and color
            is_visible = distance <= LIGHT_RANGE**2 * CELL_SIZE**2
            base_color = SEEN if visibility[y][x] else UNSEEN

            # Drawing walls
            if maze[y][x] == 1:
                color = visibility[y][x] if is_visible else base_color
                pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

            # Crystals
            elif maze[y][x] == 2:
                crystal_color = (0, 255, 255) if crystal_blink_state and is_visible else (255, 255, 255)  # Blue/Cyan when blinking, else white
                color = crystal_color if is_visible else base_color
                pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

            # Exit
            elif maze[y][x] == 3:
                color = GREEN if is_visible else base_color
                pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

            # Active monster
            elif monsters[y][x] == 1:
                if target_monster == (x, y):
                    color = (255, 0, 0) if monster_blink_state else monster_visibility[y][x]  # Red color for blinking
                else:
                    color = monster_visibility[y][x]

                color = color if is_visible else base_color
                pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

            # Dead monster
            elif monsters[y][x] == 2:
                pygame.draw.rect(screen, PINK, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def valid_move(x, y, maze):
    '''
    Determine if a move is valid based on the coordinates and maze structure.

    Args:
        x, y (int): Desired coordinates for movement.
        maze (list): 2D list representation of the maze.

    Returns:
        bool: True if the move is valid, False otherwise.
    '''
    if x < 0 or y < 0 or x >= COLS or y >= ROWS:
        return False
    return maze[y][x] != 1


def move_monster(monster_x, monster_y, player_x, player_y, maze):
    '''
    Calculate a single monster's new position based on the player's position.

    Args:
        monster_x, monster_y (int): Current coordinates of the monster.
        player_x, player_y (int): Current coordinates of the player.
        maze (list): 2D list representation of the maze.

    Returns:
        tuple: New coordinates (x, y) of the monster.
    '''
    dx, dy = 0, 0

    if monster_x < player_x and valid_move(monster_x + 1, monster_y, maze):
        dx = 1
    elif monster_x > player_x and valid_move(monster_x - 1, monster_y, maze):
        dx = -1

    if monster_y < player_y and valid_move(monster_x, monster_y + 1, maze):
        dy = 1
    elif monster_y > player_y and valid_move(monster_x, monster_y - 1, maze):
        dy = -1

    return monster_x + dx, monster_y + dy


def move_monsters(monsters, player_x, player_y, maze, visibility):
    '''
    Move all monsters in the player's visible range. Monsters move toward the player
    if they are in the visible range, otherwise they remain in their current positions.
    Dead monsters stay in their positions.

    Args:
        monsters (list): 2D list representing the current state of monsters.
        player_x, player_y (int): Current coordinates of the player.
        maze (list): 2D list representation of the maze.
        visibility (list): 2D list indicating which tiles are currently visible.

    Returns:
        list: A 2D list representing the updated state of monsters.
    '''
    new_monsters = [[0 for _ in range(COLS)] for _ in range(ROWS)]

    for y in range(len(monsters)):
        for x in range(len(monsters[y])):
            if monsters[y][x] == 1:
                # If the monster is visible
                if visibility[y][x]:
                    new_x, new_y = move_monster(x, y, player_x, player_y, maze)
                    new_monsters[new_y][new_x] = 1
                else:
                    new_monsters[y][x] = 1
            elif monsters[y][x] == 2:  # Dead monster
                new_monsters[y][x] = 2  # Retain the dead monster in its current position

    return new_monsters


def has_wall_between(x1, y1, x2, y2, maze):
    '''
    Determine if there's a wall between two given points using Bresenham's Line Algorithm.

    Args:
        x1, y1 (int): Starting point coordinates.
        x2, y2 (int): Ending point coordinates.
        maze (list): 2D list representation of the maze.

    Returns:
        bool: True if there's a wall between the points, False otherwise.
    '''
    points = bresenham_line(x1, y1, x2, y2)

    for (px, py) in points:
        if maze[py][px] == 1:
            return True
    return False


def shoot_bullet(px, py, target):
    '''
    Simulate shooting a bullet from a player to a target. If a monster is hit,
    it's marked as dead. Sound effects and messages are played accordingly.

    Args:
        px, py (int): Player's current coordinates.
        target (tuple): Target point's coordinates.
    '''
    global score  # Access the global score variable
    score += monster_value  # Increment the score for shooting a monster

    gunshot_sound.play()
    tx, ty = target
    print(f"SHOOTING: Aimed and fired at ({tx}, {ty})")

    if has_wall_between(px, py, tx, ty, maze):
        print(f"SHOOTING: Bullet hit a wall before reaching target at ({tx}, {ty}).")
        return

    # Check for monster collision using Bresenham's Line Algorithm
    points = bresenham_line(px, py, tx, ty)
    for (bullet_x, bullet_y) in points:
        if monsters[bullet_y][bullet_x] == 1:
            monsters[bullet_y][bullet_x] = 2
            dead_monsters.append((bullet_x, bullet_y))
            print(f"SHOOTING: Hit monster at ({bullet_x}, {bullet_y})")
            handle_monster_death(insults)
            return  # Stop the bullet after hitting a monster

    print(f"SHOOTING: Bullet reached its target  ({tx}, {ty}) without hitting a monster.")


def bresenham_line(x1, y1, x2, y2):
    '''
    Use Bresenham's Line Algorithm to return all points between two given points.

    Args:
        x1, y1 (int): Starting point coordinates.
        x2, y2 (int): Ending point coordinates.

    Returns:
        list: List of coordinates (x, y) between the start and end points.
    '''
    points = []
    is_steep = abs(y2 - y1) > abs(x2 - x1)
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    dx = x2 - x1
    dy = y2 - y1
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1
    y = y1
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    if swapped:
        points.reverse()

    return points


def find_closest_monster(px, py, monsters, maze):
    '''
    Find the closest monster to the player that is within the light range and
    does not have a wall between the player and the monster.

    Args:
        px (int): Player's x-coordinate.
        py (int): Player's y-coordinate.
        monsters (list): 2D list representation of the monsters in the maze.
        maze (list): 2D list representation of the maze.

    Returns:
        tuple: (x, y) coordinates of the closest monster or None if no monster is found.
    '''
    closest_monster = None
    closest_distance = float("inf")

    for y in range(len(monsters)):
        for x in range(len(monsters[y])):
            if monsters[y][x] == 1:
                distance = ((x - px) ** 2 + (y - py) ** 2) ** 0.5
                if distance < closest_distance and not has_wall_between(px, py, x, y, maze) and distance <= LIGHT_RANGE:
                    closest_monster = (x, y)
                    closest_distance = distance

    return closest_monster


def search_corpse(messages):
    '''
    Adds a random message from the given list when a corpse is searched.

    Args:
        messages (list): List of possible messages.
    '''
    add_message('search_corpse', random.choice(messages), RED, 1000)


def handle_monster_death(messages):
    '''
    Adds a random message from the given list when a monster is killed.

    Args:
        messages (list): List of possible messages related to monster death.
    '''
    add_message('handle_monster_death', random.choice(messages), RED, 1500)


def clear_screen():
    '''
    Clears the game screen.

    Fills the screen with a background color, typically black or white.
    If a background image is available, it can be blitted instead.
    '''
    screen.fill(BLACK)
    pygame.display.flip()


@timer_decorator
def play_random_ambient():
    track = random.choice([ambient1_sound, ambient2_sound, ambient3_sound])
    track.play()


@timer_decorator
def play_random_cough(messages):

    # play random cough
    track = random.choice([cough0_sound, cough1_sound, cough2_sound, cough3_sound, cough4_sound])
    track.play()                    # if using base64 files, if direct.ogg then use pygame.mixer.music.load(track) and .play(1)

    # show random cough message
    add_message('play_random_cough', random.choice(messages), COUGH, 1500)


def post_movement_processing():
    '''
    Process events and calculations after player's movement.

    Adjusts game states like loop counter, monster and crystal blink states,
    score, and monster positions. Updates visibility arrays and handles
    various collisions (monsters, crystals, exit). Plays step sound when needed.
    '''
    global loop_counter, monster_blink_state, crystal_blink_state, visibility, monster_visibility, score, monsters

    if player_moved:
        score -= 1
        loop_counter = 0
        monsters = move_monsters(monsters, player_x, player_y, maze, visibility)
        check_for_monster_collision()
        check_for_crystal_collision(crystal_value)
        check_for_exit_collision(exit_value)
        step_sound.play()

    loop_counter += 1

    if loop_counter >= toxicity_value:
        score -= 1
        loop_counter = 0

    monster_blink_state = not monster_blink_state
    crystal_blink_state = not crystal_blink_state
    visibility, monster_visibility = update_visibility_arrays(
        light_x, light_y, LIGHT_RANGE, COLS, ROWS, visibility, monster_visibility)


def check_end_conditions():
    '''
    Checks and handles game end conditions.

    Terminates the game if the player's score reaches certain criteria.
    Triggers random events at specific score intervals.
    '''
    #global score, game_running, game_ended
    global score

    if score <= 0:
        terminate_game("points")

    if score % 99 == 0 and not game_ended:
        score -= 1
        random_pick = random.choice(["coughing", "searching"])

        if random_pick == "coughing":
            play_random_cough(cough_banter)
        elif random_pick == "searching":
            add_message('check_end_conditions', random.choice(found_gem), BLUE, 1500)


def display_loading_screen(base64_image_string):
    # This function displays a simple loading screen

    # Decode the base64 string to bytes
    image_bytes = base64.b64decode(base64_image_string)
    image_file = io.BytesIO(image_bytes)


    # Load the image from the file-like object
    background_image = pygame.image.load(image_file)
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))  # Scale image to fit screen

    # Draw the background image
    screen.blit(background_image, (0, 0))

    # Set up font and render the text
    font = pygame.font.SysFont(None, 55)
    text = font.render('Loading...', True, (255, 255, 255))
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))

    # Update the display
    pygame.display.flip()
    pygame.time.wait(1000)

def exit_game():
    pygame.quit()
    sys.exit()


# Display the loading screen while save files are encoded
display_loading_screen(assets.BASE64_IMG_PIRATE)


@timer_decorator
def make_wav_from_base64(base64input):
    '''
    Converts a base64 encoded string to a WAV sound.

    Decodes the given base64 string into bytes, then loads it into
    pygame's Sound object. This allows storing WAV files as strings
    and converting them to sound objects at runtime.

    Args:
        base64input (str): The base64 encoded string representation of the WAV file.

    Returns:
        pygame.mixer.Sound: A sound object that can be played in pygame.
    '''
    decoded_wav = base64.b64decode(base64input)
    byte_io = io.BytesIO(decoded_wav)
    return pygame.mixer.Sound(file=byte_io)


# load base64 into wav file in memory.
# refactor how to do this, doubles memory usage?
# What problem am I solving besides bundling the assets?
# Load a sound effect
# sound = pygame.mixer.Sound('assets/bleh.ogg')
step_sound = make_wav_from_base64(assets.BASE64_STEP)
new_sound = make_wav_from_base64(assets.BASE64_NEW)
goblin_sound = make_wav_from_base64(assets.BASE64_GOBLIN)
gunshot_sound = make_wav_from_base64(assets.BASE64_GUNSHOT)
crystals_sound = make_wav_from_base64(assets.BASE64_CRYSTALS)
ambient1_sound = make_wav_from_base64(assets.BASE64_AMBIENT1)
ambient2_sound = make_wav_from_base64(assets.BASE64_AMBIENT2)
ambient3_sound = make_wav_from_base64(assets.BASE64_AMBIENT3)
cough0_sound = make_wav_from_base64(assets.BASE64_COUGH0)
cough1_sound = make_wav_from_base64(assets.BASE64_COUGH1)
cough2_sound = make_wav_from_base64(assets.BASE64_COUGH2)
cough3_sound = make_wav_from_base64(assets.BASE64_COUGH3)
cough4_sound = make_wav_from_base64(assets.BASE64_COUGH4)

# ok, startup game, generate and start main loop
load_next_level(player_x, player_y)
terminate_after_message = False

try:
    # show help message first
    game_ended = False
    first_run = True  # Initialize this flag to True
    handle_paused_game()

    # -------- Main Program Loop -----------
    while game_running:
        player_moved = False  # Flag to check if player moved

        for event in pygame.event.get():
            # Capture the mouse's motion event
            if event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos

            if event.type == pygame.QUIT:
                game_running = False

            elif event.type == pygame.KEYDOWN:
                # Check for Ctrl+C key combination
                if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    print("Received Ctrl+C, terminating game...")
                    terminate_game()
                    game_running = False
                    continue

                if event.key == pygame.K_p:
                    paused = not paused

                # Separate handling for when the game is paused
                if paused:
                    if first_run:
                        first_run = False
                        handle_paused_game()
                    else:
                        handle_paused_game()
                    continue

                if event.key == pygame.K_ESCAPE:
                    terminate_game()
                    terminate_after_message = True

                if event.key == pygame.K_TAB:
                    target_monster = find_closest_monster(player_x, player_y,
                                                          monsters, maze)
                    print(f"AIMING: Targeting monster at {target_monster}")

                elif event.key == pygame.K_SPACE and target_monster:
                    shoot_bullet(player_x, player_y, target_monster)
                    player_moved = True

                else:
                    prev_x, prev_y = player_x, player_y

                    if not terminate_after_message:
                        player_x, player_y, light_x, light_y = move_player(
                            event, maze, player_x, player_y, light_x, light_y, paused)

                        # Set player_moved flag if position changed
                        player_moved = (prev_x, prev_y) != (player_x, player_y)

        # Handle events after player movement
        post_movement_processing()

        # Update screen visuals
        draw_game_screen(
            screen, player_x, player_y, light_x, light_y, maze, visibility,
            monsters, monster_visibility, SEEN, UNSEEN, target_monster,
            monster_blink_state, crystal_blink_state, mouse_x, mouse_y, score, font)

        draw_messages()

        if terminate_after_message and not current_message and not message_queue:
            game_running = False

        pygame.display.flip()  # Update the screen
        clock.tick(30)  # Limit to 30 frames per second
        check_end_conditions()  # Check game end conditions

except KeyboardInterrupt:
    print("Received KeyboardInterrupt, terminating game...")
    terminate_game()  # Your function to terminate the game gracefully

exit_game()
