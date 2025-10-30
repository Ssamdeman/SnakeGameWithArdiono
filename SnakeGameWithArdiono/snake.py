import pygame
import random
import serial
import time

# --- Constants ---
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# --- Colors ---
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GRID_LINE_COLOR = (50, 50, 50)

# --- Pygame Init ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Arduino Snake Game")
clock = pygame.time.Clock()

# --- Serial Setup ---
def init_serial(port='COM3'):
    try:
        ser = serial.Serial(port, 9600, timeout=1)
        time.sleep(2)
        print("✅ Serial connected.")
        return ser
    except Exception as e:
        print(f"⚠️ Serial error: {e}")
        return None

ser = init_serial('COM3')  # Change this to your port

# --- Game State ---
snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
direction = (1, 0)  # Start moving right
food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
score = 0
game_over = False

# --- Functions ---
def draw_grid():
    screen.fill(BLACK)
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRID_LINE_COLOR, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRID_LINE_COLOR, (0, y), (SCREEN_WIDTH, y))

def draw_snake():
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_food():
    pygame.draw.rect(screen, RED, (food[0] * GRID_SIZE, food[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def move_snake():
    global snake
    head_x, head_y = snake[0]
    new_head = (head_x + direction[0], head_y + direction[1])

    # Wrapping walls
    new_head = (
        new_head[0] % GRID_WIDTH,
        new_head[1] % GRID_HEIGHT
    )

    snake.insert(0, new_head)

def check_collision():
    global game_over
    head = snake[0]
    if head in snake[1:]:
        game_over = True

def handle_food():
    global food, score
    if snake[0] == food:
        score += 1
        while True:
            new_food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if new_food not in snake:
                food = new_food
                break
    else:
        snake.pop()

def draw_score():
    font = pygame.font.SysFont("Arial", 20)
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (5, 5))

def game_over_screen():
    screen.fill(BLACK)
    font_large = pygame.font.SysFont("Arial", 50)
    font_small = pygame.font.SysFont("Arial", 25)
    text1 = font_large.render("Game Over!", True, RED)
    text2 = font_small.render(f"Final Score: {score}", True, WHITE)
    screen.blit(text1, (SCREEN_WIDTH // 2 - text1.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
    pygame.display.flip()
    pygame.time.wait(3000)

# --- Main Loop ---
while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True

    # --- Joystick Input (Robust Parsing) ---
    if ser and ser.in_waiting > 0:
        try:
            line = ser.read_until(b'\n').decode('utf-8', errors='ignore').strip()
            
            # Debug: Print raw line to see what we're getting
            # print(f"Raw line: '{line}'")
            
            if line:  # Only process non-empty lines
                parts = line.split(',')
                if len(parts) == 3:
                    # Strip whitespace and check if parts are not empty
                    x_str, y_str, button_str = [p.strip() for p in parts]
                    
                    if x_str and y_str and button_str:  # Make sure none are empty
                        x = int(x_str)
                        y = int(y_str)
                        button = int(button_str)
                        
                        # Debug: Print parsed values
                        print(f"Parsed - X: {x}, Y: {y}, Button: {button}")
                        
                        # Map joystick to direction (with proper constraints)
                        if x < 400 and direction != (1, 0):  # Left
                            direction = (-1, 0)
                        elif x > 600 and direction != (-1, 0):  # Right
                            direction = (1, 0)
                        elif y < 400 and direction != (0, 1):  # Up
                            direction = (0, -1)
                        elif y > 600 and direction != (0, -1):  # Down
                            direction = (0, 1)
                    else:
                        print("⚠️ Empty parts in data")
                else:
                    print(f"⚠️ Invalid number of parts: {len(parts)} - Line: '{line}'")
        except ValueError as e:
            print(f"⚠️ Value error: {e} - Line: '{line}'")
        except Exception as e:
            print(f"⚠️ Other serial error: {e}")

    # --- Game Logic ---
    move_snake()
    handle_food()
    check_collision()

    # --- Draw Everything ---
    draw_grid()
    draw_snake()
    draw_food()
    draw_score()
    pygame.display.flip()
    clock.tick(10)  # Control game speed

game_over_screen()
pygame.quit()