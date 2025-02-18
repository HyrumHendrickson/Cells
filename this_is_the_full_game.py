import pygame
import sys
import random
import numpy
import string

# Initialize Pygame
pygame.init()

# Core game configuration
GRID_SIZE = 50  # Number of cells in both width and height of the grid
CELL_SIZE = 16  # Size of each cell in pixels - smaller values create a more detailed but smaller view
SCREEN_SIZE = GRID_SIZE * CELL_SIZE  # Calculate total screen dimensions
FPS = 10  # Controls simulation speed - higher values make the simulation run faster

# Define colors for different cell states
WHITE = (200, 200, 200)  # Empty cells
BLACK = (0, 0, 0)        # Wall cells
BLUE = (100, 100, 200)   # Rock cells
RED = (200, 100, 100)    # Paper cells
GREEN = (100, 200, 100)  # Scissors cells

# Game state constants
EMPTY = 'EMPTY'      # Represents an empty cell
ROCK = 'ROCK'       # Represents a rock cell
PAPER = 'PAPER'      # Represents a paper cell
SCISSORS = 'SCISSORS'   # Represents a scissors cell
WALL = 'WALL'       # Represents a wall/obstacle cell
RANDOM = 'RANDOM'   # Mode for generating cells randomly (limited to rock/paper/scissors)
REAL_RANDOM = "REAL_RANDOM"  # Mode for generating cells randomly (includes walls and empty cells)
STATE_ORDER = [EMPTY, WALL, ROCK, PAPER, SCISSORS]  # Defines the order for cycling through states when clicking

# Global game settings
state_on = RANDOM    # Current placement mode for generating new cells
diagonal_constant = False       # If True, considers all 8 surrounding cells; if False, only considers 4 adjacent cells
stable_constant = True        # If True, cells survive when surrounded by both predator and prey; if False, they die
place_color = True   # If True, clicking cycles through RPS states; if False, toggles between wall and empty
dark_range = {"x1": 3, "y1": 0, "xjump":10, "yjump":10} #
highlight = 0

history = []

# Constants for base conversion
BASE5_CHARS = ['0', '1', '2', '3', '4']
BASE62_CHARS = string.digits + string.ascii_lowercase + string.ascii_uppercase

def get_element():
    ## Returns a cell state based on the current state_on setting.
    ## Used when generating new cells or resetting the grid.
    if state_on == RANDOM:
        return random.choice(STATE_ORDER[2:])  # Only choose between rock, paper, scissors
    elif state_on == REAL_RANDOM:
        return random.choice(STATE_ORDER)      # Can choose any state including walls and empty
    else: 
        return state_on                        # Return the specific selected state

def new_grid(width, height):
    # Creates a new grid filled with elements based on the current state_on setting.
    # Returns a 2D list representing the game grid.
    return numpy.array([[get_element() for _ in range(width)] for _ in range(height)], dtype =object)




# Initialize the game grid
grid = new_grid(GRID_SIZE, GRID_SIZE)

# Set up the Pygame display
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("ROPAS")

# Clock object to control game speed
clock = pygame.time.Clock()

def draw_grid():
    # Draws the current state of the grid to the screen.
    # Each cell type is represented by a different color:
    # Rock: Blue
    # Paper: Red
    # Scissors: Green
    # Wall: Black
    # Empty: White
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            cell = grid[y][x]
            cell_rect = (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = WHITE
            if cell == ROCK:
                color = BLUE
            elif cell == PAPER:
                color = RED
            elif cell == SCISSORS:
                color = GREEN
            elif cell == WALL:
                color = BLACK
            if(highlight and dark_range["x1"] < x and x < dark_range["x1"] + dark_range["xjump"] and dark_range["y1"] < y and y < dark_range["y1"] + dark_range["yjump"] ):
                color = tuple(a + b for a, b in zip(color, (50,50,50)))
                
            pygame.draw.rect(screen, color, cell_rect)

def get_neighbors(x, y):
    #Returns a list of neighboring cell states for the cell at (x, y).
    #If diagonal_constant is False: Returns only orthogonal neighbors (up, down, left, right)
    #If diagonal_constant is True: Returns all 8 surrounding neighbors (including diagonals)
    #Walls are excluded from the neighbor list and edges of the grid are respected.
    if not diagonal_constant:
        neighbors = []
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # Up, Down, Left, Right
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and grid[ny][nx] != WALL:
                neighbors.append(grid[ny][nx])
        
        return neighbors
    else:
        neighbors = []
        # Check all 8 surrounding cells
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dx == 0 and dy == 0:  # Skip the center cell
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and grid[ny][nx] != WALL:
                    neighbors.append(grid[ny][nx])
        return neighbors

def update_grid():
    # Updates the grid based on Rock-Paper-Scissors rules:
    # - Empty cells become the type that has the most neighbors
    # - Cells change to their predator's type if only the predator is present
    # - If both predator and prey are present:
    #     - If stable is True: Cell maintains its current state
    #     - If stable is False: Cell becomes empty
    # The rules follow a circular pattern:
    # Rock beats Scissors, Scissors beats Paper, Paper beats Rock
    global grid
    new_grid = numpy.array([[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)], dtype=object)
    
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            current_state = grid[y][x]
            
            # Count the number of each type of neighbor
            neighbors = get_neighbors(x, y)
            rock_count = neighbors.count(ROCK)
            paper_count = neighbors.count(PAPER)
            scissors_count = neighbors.count(SCISSORS)

            if current_state == EMPTY:
                # Empty cell becomes the type with the most neighbors
                if rock_count > paper_count and rock_count > scissors_count:
                    new_grid[y][x] = ROCK
                elif paper_count > rock_count and paper_count > scissors_count:
                    new_grid[y][x] = PAPER
                elif scissors_count > rock_count and scissors_count > paper_count:
                    new_grid[y][x] = SCISSORS
                else:
                    new_grid[y][x] = EMPTY  # Maintain empty state if there's a tie
            else:
                # Check if cell is surrounded by both predator and prey
                surrounded_by_both = (
                    (current_state == ROCK and paper_count > 0 and scissors_count > 0) or
                    (current_state == PAPER and rock_count > 0 and scissors_count > 0) or
                    (current_state == SCISSORS and rock_count > 0 and paper_count > 0)
                )
                
                if surrounded_by_both:
                    new_grid[y][x] = current_state if stable_constant else EMPTY
                else:
                    # Apply specific transformations based on RPS rules
                    if current_state == ROCK and paper_count > 0 and scissors_count == 0:
                        new_grid[y][x] = PAPER  # Paper beats Rock
                    elif current_state == PAPER and scissors_count > 0 and rock_count == 0:
                        new_grid[y][x] = SCISSORS  # Scissors beats Paper
                    elif current_state == SCISSORS and rock_count > 0 and paper_count == 0:
                        new_grid[y][x] = ROCK  # Rock beats Scissors
                    else:
                        new_grid[y][x] = current_state  # Maintain current state if no transformation applies

            # Walls always remain unchanged
            if current_state == WALL:
                new_grid[y][x] = WALL

    grid = new_grid

def toggle_cell(x, y):
    # Handles mouse clicks on cells:
    # - If place_color is True: Cycles through Rock, Paper, Scissors states
    # - If place_color is False: Toggles between Wall and Empty states
    current_state = grid[y][x]
    if place_color:
        # Cycle through RPS states (excluding Wall and Empty)
        new_state = STATE_ORDER[((STATE_ORDER.index(current_state) - 1) % (len(STATE_ORDER)-2))+2]
        grid[y][x] = new_state

    else:
        # Toggle between Wall and Empty
        grid[y][x] = WALL if current_state != WALL else EMPTY

BASE62_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def grid_to_base62(grid):
    # Step 1: Get the height and width of the grid
    height, width = grid.shape

    # Step 2: Convert the height and width to base 5 strings (3 digits each)
    height_base5 = base10_to_base5(height)
    width_base5 = base10_to_base5(width)

    # Combine height and width as the first 6 digits (3 digits each)
    dimension_str = height_base5.zfill(3) + width_base5.zfill(3)

    # Step 3: Convert grid to a single base 5 number
    base5_number = 0
    for row in grid:
        for cell in row:
            cell_value = STATE_ORDER.index(cell)  # Convert cell type to a base 5 digit (0-4)
            base5_number = base5_number * 5 + cell_value

    # Step 4: Convert base 5 number to base 62
    base62_number = ""
    while base5_number > 0:
        remainder = base5_number % 62
        base62_number = BASE62_CHARS[remainder] + base62_number
        base5_number //= 62

    # Step 5: Combine the dimension string with the grid's base 62 string
    return dimension_str + base62_number

def base10_to_base5(number):
    """Converts a base 10 number to a base 5 string."""
    base5_number = ""
    while number > 0:
        remainder = number % 5
        base5_number = str(remainder) + base5_number
        number //= 5
    return base5_number

def base62_to_grid(base62_str):
    # Step 1: Extract the first 6 characters for height and width in base 5
    height_base5 = base62_str[:3]
    width_base5 = base62_str[3:6]
    
    # Convert them back to base 10 (height and width in base 5)
    height = base5_to_base10(height_base5)
    width = base5_to_base10(width_base5)
    
    # Step 2: Convert the remaining part of the string to a base 62 number
    base5_number = 0
    for char in base62_str[6:]:
        base5_number = base5_number * 62 + BASE62_CHARS.index(char)

    # Step 3: Convert base 5 number back to grid
    new_grid = numpy.array([[STATE_ORDER[0] for _ in range(width)] for _ in range(height)], dtype=object)
    for y in range(height - 1, -1, -1):
        for x in range(width - 1, -1, -1):
            cell_value = base5_number % 5
            new_grid[y][x] = STATE_ORDER[cell_value]
            base5_number //= 5

    return new_grid

def base5_to_base10(base5_str):
    """Converts a base 5 string to a base 10 number."""
    number = 0
    for char in base5_str:
        number = number * 5 + int(char)
    return number

# Save the current state of the grid to history
def save_grid_to_history():
    global history
    compressed_state = grid_to_base62(grid)
    history.append(compressed_state)
    if len(history) > 100:
        history.pop(0)  # Remove the oldest state if history exceeds 100 entries

# Restore the grid from the most recent history state
def restore_grid_from_history():
    global grid, history
    if history:
        previous_state = history.pop()
        grid = base62_to_grid(previous_state)

# Initialize a variable to store the copied shape
saved_shape = None  # Variable to store the copied shape

# Main game loop
running = True
paused = True  # Start paused to allow initial setup

print("Welcome to RPS!!")

while running:
    # Handle input events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Save the current state before any changes
                paused = not paused
                print(f"\npaused: {paused}")
            elif event.key == pygame.K_RIGHT and paused:
                # Save the current state before a manual step
                save_grid_to_history()
                update_grid()
                print(f"\nTook one step\n")
            elif event.key == pygame.K_BACKSPACE:
                highlight = (highlight + 1) % 3
            elif event.key == pygame.K_LEFT and paused:
                # Pressing the back arrow restores the previous state
                restore_grid_from_history()
                print(f"\nRestored previous state\n")
            elif event.key == pygame.K_q:
                # Q toggles between 4-neighbor and 8-neighbor mode
                diagonal_constant = not diagonal_constant
                print(f"\ndiagonal_constant (q): {diagonal_constant}\n stable_constant (w): {stable_constant}\n")
            elif event.key == pygame.K_w:
                # W toggles stability behavior
                stable_constant = not stable_constant
                print(f"\ndiagonal_constant (q): {diagonal_constant}\n stable_constant (w): {stable_constant}\n")
            elif event.key == pygame.K_TAB:
                # Tab generates a new random grid
                if not highlight:
                    grid = new_grid(GRID_SIZE, GRID_SIZE)
                    print(f"\nGenerated New grid\n")
                else:
                    grid[dark_range["y1"]+1: dark_range["y1"]+ dark_range["yjump"], dark_range["x1"]+1: dark_range["x1"] + dark_range["xjump"]] = new_grid(dark_range["xjump"]-1, dark_range["yjump"]-1)
                save_grid_to_history()
            elif event.key == pygame.K_RSHIFT:
                # Right Shift toggles between placing colors (RPS) and walls
                place_color = not place_color
                print(f"\nplace_color (RSHIFT): {place_color}\n")
            elif event.key == pygame.K_LSHIFT:
                # Left Shift cycles through placement modes
                if state_on == STATE_ORDER[-1]:
                    state_on = RANDOM
                elif state_on == RANDOM:
                    state_on = REAL_RANDOM
                elif state_on == REAL_RANDOM:
                    state_on = STATE_ORDER[0]
                else:
                    state_on = STATE_ORDER[STATE_ORDER.index(state_on) + 1]
                print(f"\nSTATE_ON: {state_on}")
            elif event.key == pygame.K_BACKSPACE:
                highlight = (highlight + 1) % 3
            elif event.key == pygame.K_o and highlight:
                # Save the currently highlighted area to memory
                x_start = dark_range["x1"] + 1
                y_start = dark_range["y1"] + 1
                x_end = x_start + dark_range["xjump"] - 1
                y_end = y_start + dark_range["yjump"] - 1
                saved_shape = grid[y_start:y_end, x_start:x_end].copy()
                print("Highlighted area saved to memory.")
                compressed_shape = grid_to_base62(saved_shape)
                print(f"Compressed string of the saved shape: {compressed_shape}")

            elif event.key == pygame.K_p and highlight and saved_shape is not None:
                # Paste the saved shape at the current highlighted position
                x_start = dark_range["x1"] + 1
                y_start = dark_range["y1"] + 1
                x_end = min(x_start + saved_shape.shape[1], GRID_SIZE)
                y_end = min(y_start + saved_shape.shape[0], GRID_SIZE)
                # Ensure the paste area does not exceed grid bounds
                grid[y_start:y_end, x_start:x_end] = saved_shape[:y_end - y_start, :x_end - x_start]
                save_grid_to_history()
                print("Saved shape pasted at the new position.")

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Prompt the user to input a compressed string
                    compressed_input = input("Enter a compressed string to load the saved shape: ")
                    
                    
                    # Try to load the shape from the compressed string
                    if(len(compressed_input) > 8):
                        loaded_grid = base62_to_grid(compressed_input)
                        saved_shape = loaded_grid  # Store the loaded shape in saved_shape
                    
                    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            grid_x, grid_y = x // CELL_SIZE, y // CELL_SIZE
            if not highlight:
                # Handle mouse clicks when paused
                toggle_cell(grid_x, grid_y)
                save_grid_to_history()
            else:
                if highlight == 1:
                    dark_range["x1"] = grid_x - 1; dark_range["y1"] = grid_y - 1
                    while dark_range["x1"] + dark_range["xjump"] > GRID_SIZE:
                        dark_range["xjump"] -= 1
                    while dark_range["y1"] + dark_range["yjump"] > GRID_SIZE:
                        dark_range["yjump"] -= 1
                else: 
                    newx = grid_x - dark_range["x1"] + 1; newy = grid_y - dark_range["y1"] + 1
                    if dark_range["x1"] < grid_x and dark_range["y1"] < grid_y:
                        dark_range["xjump"] = newx; dark_range["yjump"] = newy

    # Update game state if not paused
    if not paused:
        update_grid()
        save_grid_to_history()

    # Draw the current state
    screen.fill(WHITE)
    draw_grid()
    pygame.display.flip()

    # Control the game speed
    clock.tick(FPS)

print("Thanks for playing RPS!!")
