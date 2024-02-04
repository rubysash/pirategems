import pygame

def move_player(event, maze, player_x, player_y, light_x, light_y, paused):
    if paused:
        return player_x, player_y, light_x, light_y

    # Check if Shift is held down
    shift_pressed = pygame.key.get_mods() & (pygame.KMOD_LSHIFT | pygame.KMOD_RSHIFT)

    # Movement amount
    move_amount = 3 if shift_pressed else 1

    # Movement logic
    def can_move(x, y):
        if 0 <= x < len(maze[0]) and 0 <= y < len(maze):
            return maze[y][x] != 1
        return False

    if event.key in [pygame.K_LEFT, pygame.K_KP4]:
        for i in range(1, move_amount + 1):
            if can_move(player_x - i, player_y):
                player_x -= 1
                light_x -= 1
            else:
                break

    elif event.key in [pygame.K_RIGHT, pygame.K_KP6]:
        for i in range(1, move_amount + 1):
            if can_move(player_x + i, player_y):
                player_x += 1
                light_x += 1
            else:
                break

    elif event.key in [pygame.K_UP, pygame.K_KP8]:
        for i in range(1, move_amount + 1):
            if can_move(player_x, player_y - i):
                player_y -= 1
                light_y -= 1
            else:
                break

    elif event.key in [pygame.K_DOWN, pygame.K_KP2]:
        for i in range(1, move_amount + 1):
            if can_move(player_x, player_y + i):
                player_y += 1
                light_y += 1
            else:
                break

    elif event.key == pygame.K_KP7:  # Top-left
        for i in range(1, move_amount + 1):
            if can_move(player_x - i, player_y - i):
                player_x -= 1
                player_y -= 1
                light_x -= 1
                light_y -= 1
            else:
                break

    elif event.key == pygame.K_KP9:  # Top-right
        for i in range(1, move_amount + 1):
            if can_move(player_x + i, player_y - i):
                player_x += 1
                player_y -= 1
                light_x += 1
                light_y -= 1
            else:
                break

    elif event.key == pygame.K_KP1:  # Bottom-left
        for i in range(1, move_amount + 1):
            if can_move(player_x - i, player_y + i):
                player_x -= 1
                player_y += 1
                light_x -= 1
                light_y += 1
            else:
                break

    elif event.key == pygame.K_KP3:  # Bottom-right
        for i in range(1, move_amount + 1):
            if can_move(player_x + i, player_y + i):
                player_x += 1
                player_y += 1
                light_x += 1
                light_y += 1
            else:
                break

    return player_x, player_y, light_x, light_y