import random
from variables import *

def recursive_backtracking(ROWS, COLS, player_x, player_y):
    '''
    draws the maze walls using recursive_backtracking
    '''
    # Initialize the maze with all walls
    start_x, start_y = player_x, player_y
    maze = [[1 for x in range(COLS)] for y in range(ROWS)]

    # Mark the starting point as visited
    maze[start_y][start_x] = player_x, player_y

    # Run the recursive backtracking algorithm
    stack = [(start_x, start_y)]
    while len(stack) > 0:
        x, y = stack[-1]
        neighbors = []
        if x > 1 and maze[y][x-1] == 1:
            neighbors.append((x-1, y))
        if x < COLS-2 and maze[y][x+1] == 1:
            neighbors.append((x+1, y))
        if y > 1 and maze[y-1][x] == 1:
            neighbors.append((x, y-1))
        if y < ROWS-2 and maze[y+1][x] == 1:
            neighbors.append((x, y+1))

        if len(neighbors) > 0:
            nx, ny = random.choice(neighbors)
            corridor_length = random.randint(2, 7)
            for i in range(1, corridor_length):
                if nx == x:
                    if y+i*(ny-y)>=0 and y+i*(ny-y) < ROWS:
                        maze[y+i*(ny-y)][x] = 0
                elif ny == y:
                    if x+i*(nx-x)>=0 and x+i*(nx-x) < COLS:
                        maze[y][x+i*(nx-x)] = 0
            maze[ny][nx] = 0
            stack.append((nx, ny))
        else:
            stack.pop()
    return maze

def distance(x1, y1, x2, y2):
    '''
    Eucledean Distance Test to calculate distance
    '''
    return ((x1-x2)**2 + (y1-y2)**2)**0.5

def set_monsters(maze, player_x, player_y, monster_density):
    '''
    Makes a 2d array and then puts monsters in it
    Skips over places with substance in it.
    Ensures monsters aren't too close to the player start.
    '''
    # predefine a bunch of zeros in the 2d array
    monsters = [[0 for x in range(COLS)] for y in range(ROWS)]

    # then loop over the maze to see where open space is
    for y in range(len(maze)):
        for x in range(len(maze[y])):

            # if there is open space here and not too close to the player
            if maze[y][x] == 0 and distance(x, y, player_x, player_y) > LIGHT_RANGE:

                # and passes random threshold
                num = random.randint(1, 100)
                if num < monster_density:  # percentage of "monster" appearing

                    # then load it into 2d monster array as existing
                    monsters[y][x] = 1
    return monsters

def set_exit(maze, player_x, player_y):
    '''
    Sets an exit point in the maze in an open space.
    Ensures the exit is not too close to the player's start position.
    The exit is represented by the number 3.
    '''
    while True:
        x = random.randint(0, COLS - 1)
        y = random.randint(0, ROWS - 1)
        
        if maze[y][x] == 0 and distance(x, y, player_x, player_y) > LIGHT_RANGE:  # open space and not too close to player
            maze[y][x] = 3  # set exit
            break
    return maze

def set_crystals(maze, number_of_crystals=5):
    '''
    Sets crystals in the maze in open spaces.
    Crystals are represented by the number 2.
    The default number of crystals is 5, but can be changed.
    '''
    placed_crystals = 0
    while placed_crystals < number_of_crystals:
        x = random.randint(0, COLS - 1)
        y = random.randint(0, ROWS - 1)
        
        if maze[y][x] == 0:  # open space
            maze[y][x] = 2  # set crystal
            placed_crystals += 1
    return maze
