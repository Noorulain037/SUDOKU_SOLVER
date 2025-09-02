import pygame
import time
import random
import copy
import os
import json
from leaderboard import load_leaderboard, save_score, format_leaderboard_text

pygame.init()

# Constants
TOP_MARGIN = 60
WIDTH, HEIGHT = 540, 600 + TOP_MARGIN
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku Solver by Noor-Ul-Ain_037")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
LIGHT_RED = (255, 200, 200)

font = pygame.font.SysFont("Comic Sans MS", 32)
timer_font = pygame.font.SysFont("Comic Sans MS", 22)

selected = None
mistakes = 0
start_time = 0
paused = False
pause_start = 0
selected_number = None
total_pause_time = 0
incorrect_cells = set()

pause_button = pygame.Rect(WIDTH - 170, 15, 80, 30)
restart_button = pygame.Rect(WIDTH - 85, 15, 80, 30)
remove_button = pygame.Rect(10, 15, 100, 30)

DIFFICULTY_LEVELS = {
    "Easy": 35,
    "Medium": 45,
    "Hard": 55
}
current_level = "Medium"

# Load sounds
correct_sound = pygame.mixer.Sound("correct.wav")
wrong_sound = pygame.mixer.Sound("wrong.wav")
win_sound = pygame.mixer.Sound("win.wav")

# Leaderboard functions
LEADERBOARD_FILE = "leaderboard.json"




def show_leaderboard():
    screen.fill(WHITE)
    leaderboard = load_leaderboard()
    title = font.render("Leaderboard", True, BLACK)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))

    texts = format_leaderboard_text(leaderboard, timer_font)
    for i, text_surface in enumerate(texts):
        screen.blit(text_surface, (40, 80 + i*30))

    pygame.display.update()
    pygame.time.delay(5000)


def is_valid(board, num, pos):
    row, col = pos
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(start_row, start_row + 3):
        for j in range(start_col, start_col + 3):
            if board[i][j] == num:
                return False
    return True

def find_empty(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return (i, j)
    return None

def solve(board):
    empty = find_empty(board)
    if not empty:
        return True
    row, col = empty
    nums = list(range(1, 10))
    random.shuffle(nums)
    for num in nums:
        if is_valid(board, num, (row, col)):
            board[row][col] = num
            if solve(board):
                return True
            board[row][col] = 0
    return False

def generate_board(difficulty):
    board = [[0]*9 for _ in range(9)]
    solve(board)
    full_board = copy.deepcopy(board)
    removed = 0
    total_remove = DIFFICULTY_LEVELS[difficulty]
    while removed < total_remove:
        i, j = random.randint(0, 8), random.randint(0, 8)
        if board[i][j] != 0:
            board[i][j] = 0
            removed += 1
    return board, full_board

initial_board, solved_board = generate_board(current_level)
board = [row[:] for row in initial_board]

def draw_board():
    screen.fill(WHITE)
    gap = WIDTH // 9
    for i in range(10):
        width = 4 if i % 3 == 0 else 1
        pygame.draw.line(screen, BLACK, (0, TOP_MARGIN + i*gap), (WIDTH, TOP_MARGIN + i*gap), width)
        pygame.draw.line(screen, BLACK, (i*gap, TOP_MARGIN), (i*gap, TOP_MARGIN + WIDTH), width)

    for i in range(9):
        for j in range(9):
            num = board[i][j]
            if num != 0:
                color = RED if (i, j) in incorrect_cells else BLUE if selected_number == num else BLACK
                text = font.render(str(num), True, color)
                screen.blit(text, (j * gap + 20, i * gap + 15 + TOP_MARGIN))

    if selected:
        pygame.draw.rect(screen, RED, (selected[1]*gap, TOP_MARGIN + selected[0]*gap, gap, gap), 3)

    elapsed = int(time.time() - start_time - total_pause_time) if not paused else int(pause_start - start_time - total_pause_time)
    minutes = elapsed // 60
    seconds = elapsed % 60
    timer_text = timer_font.render(f"Time: {minutes:02}:{seconds:02}", True, BLACK)
    mistakes_text = timer_font.render(f"Mistakes: {mistakes}/3", True, RED)
    screen.blit(timer_text, (120, WIDTH + 10 + TOP_MARGIN))
    screen.blit(mistakes_text, (350, WIDTH + 10 + TOP_MARGIN))

    pygame.draw.rect(screen, LIGHT_BLUE, pause_button, border_radius=6)
    screen.blit(timer_font.render("Pause", True, BLACK), pause_button.move(10, 2))

    pygame.draw.rect(screen, LIGHT_BLUE, restart_button, border_radius=6)
    screen.blit(timer_font.render("Restart", True, BLACK), restart_button.move(5, 2))

    pygame.draw.rect(screen, LIGHT_BLUE, remove_button, border_radius=6)
    screen.blit(timer_font.render("Remove", True, BLACK), remove_button.move(10, 2))

    pygame.display.update()

def is_board_full():
    return all(all(cell != 0 for cell in row) for row in board)

def show_result():
    elapsed_time = int(time.time() - start_time - total_pause_time)
    msg = "Game Over!" if mistakes >= 3 else ("Very Good!" if elapsed_time < 360 else "Good!" if elapsed_time < 600 else "Completed!")
    color = RED if mistakes >= 3 else GREEN
    result = font.render(msg, True, color)

    screen.fill(WHITE)
    screen.blit(result, (WIDTH // 2 - result.get_width() // 2, HEIGHT // 2 - 40))
    pygame.display.update()
    win_sound.play()

    pygame.time.delay(2000)

    if mistakes < 3:
        name = get_player_name()
        if not name.strip():
            name = "Anonymous"
        save_score(name, current_level, elapsed_time, mistakes)
        show_leaderboard()

    pygame.time.delay(2000)
def get_player_name():
    input_box = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 10, 200, 40)
    color_inactive = GREY
    color_active = BLUE
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    elif len(text) < 12:  # Limit name length
                        text += event.unicode

        screen.fill(WHITE)
        prompt = font.render("Enter your name:", True, BLACK)
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 - 40))

        pygame.draw.rect(screen, color, input_box, 2)
        name_surface = font.render(text, True, BLACK)
        screen.blit(name_surface, (input_box.x + 5, input_box.y + 5))
        pygame.display.update()

    return text

def restart_game():
    global board, initial_board, solved_board, selected, mistakes, start_time, paused, selected_number, total_pause_time, incorrect_cells
    initial_board, solved_board = generate_board(current_level)
    board = [row[:] for row in initial_board]
    selected = None
    mistakes = 0
    start_time = time.time()
    paused = False
    selected_number = None
    total_pause_time = 0
    incorrect_cells = set()

def select_level():
    global current_level
    choosing = True
    while choosing:
        screen.fill(WHITE)
        title = font.render("Select Difficulty", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))

        buttons = [("Easy", (WIDTH//2 - 150, 180)), ("Medium", (WIDTH//2 - 45, 180)), ("Hard", (WIDTH//2 + 60, 180))]
        for text, (x, y) in buttons:
            pygame.draw.rect(screen, LIGHT_BLUE, (x, y, 90, 40), border_radius=6)
            label = timer_font.render(text, True, BLACK)
            screen.blit(label, (x + 10, y + 10))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for text, (x, y) in buttons:
                    if x <= mx <= x+80 and y <= my <= y+40:
                        current_level = text
                        choosing = False

select_level()
restart_game()

running = True
while running:
    draw_board()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if pause_button.collidepoint(pos):
                if not paused:
                    paused = True
                    pause_start = time.time()
                else:
                    paused = False
                    total_pause_time += time.time() - pause_start

            elif restart_button.collidepoint(pos):
                restart_game()

            elif remove_button.collidepoint(pos):
                if selected:
                    i, j = selected
                    if initial_board[i][j] == 0:
                        board[i][j] = 0
                        incorrect_cells.discard((i, j))

            elif not paused and pos[1] >= TOP_MARGIN:
                x = (pos[1] - TOP_MARGIN) // (WIDTH // 9)
                y = pos[0] // (WIDTH // 9)
                if x < 9 and y < 9:
                    selected = (x, y)
                    selected_number = board[x][y] if board[x][y] != 0 else None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                restart_game()
            elif selected and not paused and pygame.K_1 <= event.key <= pygame.K_9:
                val = event.key - pygame.K_0
                i, j = selected
                if initial_board[i][j] == 0:
                    if val == solved_board[i][j]:
                        board[i][j] = val
                        incorrect_cells.discard((i, j))
                        correct_sound.play()
                        if is_board_full():
                            show_result()
                            running = False
                    else:
                        board[i][j] = val
                        incorrect_cells.add((i, j))
                        mistakes += 1
                        wrong_sound.play()
                        if mistakes >= 3:
                            show_result()
                            running = False

pygame.quit()
