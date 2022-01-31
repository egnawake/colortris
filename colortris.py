import pygame
import pygame.freetype
import random


# constants
CELL_SIZE = 60
GRID_SIZE = (7, 10)
RESOLUTION = (GRID_SIZE[0] * CELL_SIZE, GRID_SIZE[1] * CELL_SIZE)
GRAVITY_INTERVAL = 1
MOVE_INTERVAL = 0.15
PIECE_SIZE = 28
PIECE_OUTLINE_WIDTH = 4
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
SCORE_FONT_SIZE = 32


# globals
last_time = pygame.time.get_ticks()
gravity_timer = 0
gravity_multiplier = 1
move_timer = 0
can_move = True
is_scoring = False
should_spawn = True
move_dir = last_move_dir = -1
score = 0


# piece functions
def piece_new():
    color = random.randint(0, 3)
    return (color, False)

def piece_empty():
    return (-1, False)

def piece_set_active(piece, active):
    return (piece[0], active)

def piece_is_active(piece):
    return piece[1]

def piece_color(piece):
    return piece[0]

def piece_is_empty(piece):
    return piece[0] == -1


# grid functions
def grid_new(size):
    w, h = size
    grid = []

    for i in range(0, h):
        row = []
        for j in range(0, w):
            row.append(piece_empty())
        grid.append(row)

    return grid

def grid_copy(grid):
    new_grid = []

    for y in range(0, len(grid)):
        row = []
        for x in range(0, len(grid[y])):
            row.append(grid[y][x])
        new_grid.append(row)

    return new_grid

def draw_grid(screen, grid):
    for y in range(0, len(grid)):
        for x in range(0, len(grid[y])):
            p = grid[y][x]
            if not piece_is_empty(p):
                center = (x * CELL_SIZE + CELL_SIZE / 2, y * CELL_SIZE + CELL_SIZE / 2)
                pygame.draw.circle(screen, COLORS[piece_color(p)], center, PIECE_SIZE, PIECE_OUTLINE_WIDTH)


# game logic functions
def apply_gravity(grid):
    new_grid = grid_new(GRID_SIZE)

    for y in reversed(range(0, len(grid))):
        for x in range(0, len(grid[y])):
            p = grid[y][x]
            if piece_is_empty(p):
                continue
            if y < len(grid) - 1 and piece_is_empty(new_grid[y + 1][x]):
                new_grid[y + 1][x] = grid[y][x]
            else:
                new_grid[y][x] = grid[y][x]

    return new_grid

def spawn_piece(grid):
    new_grid = grid_copy(grid)

    col = random.randint(0, GRID_SIZE[0] - 1)
    p = piece_new()
    p = piece_set_active(p, True)
    new_grid[0][col] = p

    return new_grid

def move(grid, direction):
    new_grid = grid_copy(grid)

    for y in range(0, len(grid)):
        for x in range(0, len(grid[y])):
            if piece_is_active(grid[y][x])  and direction == 0 and x > 0 and piece_is_empty(grid[y][x - 1]):
                new_grid[y][x - 1] = grid[y][x]
                new_grid[y][x] = piece_empty()
            elif piece_is_active(grid[y][x])  and direction == 1 and x < len(grid[y]) - 1 and piece_is_empty(grid[y][x + 1]):
                new_grid[y][x + 1] = grid[y][x]
                new_grid[y][x] = piece_empty()

    return new_grid

def lock(grid):
    global is_scoring
    new_grid = grid_copy(grid)

    for y in range(0, len(grid)):
        for x in range(0, len(grid[y])):
            p = grid[y][x]
            if piece_is_active(p) and (y == len(grid) - 1 or not piece_is_empty(grid[y + 1][x])):
                locked = piece_set_active(p, False)
                new_grid[y][x] = locked
                is_scoring = True
                break

    return new_grid

def clear_pieces(grid):
    global is_scoring
    global should_spawn
    global score

    new_grid = grid_copy(grid)
    done = True

    start = 0
    end = start + 1

    # check horizontally
    for line in range(0, len(grid)):
        while start < len(grid[0]):
            if end < len(grid[0]) and piece_color(grid[line][start]) == piece_color(grid[line][end]):
                end = end + 1
            elif piece_color(grid[line][start]) != -1 and (end - start) >= 3:
                score += 1
                done = False
                for i in range(start, end):
                    new_grid[line][i] = piece_empty()
                start = end
                end = start + 1
            else:
                start = end
                end = start + 1
        start = 0
        end = start + 1

    # check vertically
    for col in range(0, len(grid[0])):
        while start < len(grid):
            if end < len(grid) and piece_color(grid[start][col]) == piece_color(grid[end][col]):
                end = end + 1
            elif piece_color(grid[start][col]) != -1 and (end - start) >= 3:
                score += 1
                done = False
                for i in range(start, end):
                    new_grid[i][col] = piece_empty()
                start = end
                end = start + 1
            else:
                start = end
                end = start + 1
        start = 0
        end = start + 1

    if done:
        is_scoring = False
        should_spawn = True

    return new_grid

def check_game_over(grid):
    for p in grid[0]:
        if not piece_is_empty(p) and not piece_is_active(p):
            return True
    return False


# main
def main():
    global last_time
    global gravity_timer
    global gravity_multiplier
    global move_timer
    global can_move
    global last_move_dir
    global move_dir
    global should_spawn
    global score

    # init pygame
    pygame.init()
    screen = pygame.display.set_mode((GRID_SIZE[0] * CELL_SIZE, GRID_SIZE[1] * CELL_SIZE))

    # init font
    font = pygame.freetype.Font("assets/PixelOperator.ttf")

    grid = grid_new(GRID_SIZE)

    while True:
        # event handling
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    gravity_multiplier = 0.1
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    gravity_multiplier = 1

        keys = pygame.key.get_pressed()

        # determining move direction
        if keys[pygame.K_LEFT]:
            move_dir = 0
        elif keys[pygame.K_RIGHT]:
            move_dir = 1
        else:
            move_dir = -1

        elapsed_time = (pygame.time.get_ticks() - last_time) / 1000
        last_time = pygame.time.get_ticks()

        if gravity_timer >= (GRAVITY_INTERVAL * gravity_multiplier):
            grid = apply_gravity(grid)
            grid = lock(grid)

            if is_scoring:
                grid = clear_pieces(grid)

            if should_spawn:
                grid = spawn_piece(grid)
                should_spawn = False

            if check_game_over(grid):
                exit()

            gravity_timer = 0
        else:
            gravity_timer += elapsed_time

        if move_timer >= MOVE_INTERVAL:
            can_move = True
            move_timer = 0
        elif move_dir != -1:
            move_timer += elapsed_time

        if can_move and move_dir != -1:
            grid = move(grid, move_dir)
            can_move = False

        if last_move_dir != -1 and last_move_dir != move_dir:
            can_move = True
            move_timer = 0

        last_move_dir = move_dir

        screen.fill((0, 0, 0))
        draw_grid(screen, grid)
        font.render_to(screen, (4, 4), "Score: " + str(score), (255, 255, 255), size=SCORE_FONT_SIZE)
        pygame.display.flip()


if __name__ == "__main__":
    main()

