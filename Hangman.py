import pygame
import sys
import random
import time

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangman")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
GRAY = (200, 200, 200)

# Fonts
FONT = pygame.font.Font(None, 36)
LARGE_FONT = pygame.font.Font(None, 72)
SMALL_FONT = pygame.font.Font(None, 24)

# Word lists for different age groups
WORDS_EASY = ['cat', 'dog', 'sun', 'hat', 'ball', 'tree', 'fish', 'bird', 'book', 'car']
WORDS_MEDIUM = ['python', 'hangman', 'computer', 'keyboard', 'school', 'friend', 'library', 'bicycle', 'garden', 'music']
WORDS_HARD = ['algorithm', 'parliament', 'hypothesis', 'philosophy', 'revolutionary', 'extraordinary', 'sophisticated', 'perseverance', 'enigmatic', 'serendipity']

def get_word(age):
    if age < 10:
        return random.choice(WORDS_EASY)
    elif age < 15:
        return random.choice(WORDS_MEDIUM)
    else:
        return random.choice(WORDS_HARD)

def draw_hangman(turns):
    # Draw gallows
    pygame.draw.line(screen, BLACK, (100, 400), (300, 400), 8)
    pygame.draw.line(screen, BLACK, (200, 400), (200, 100), 8)
    pygame.draw.line(screen, BLACK, (200, 100), (350, 100), 8)
    pygame.draw.line(screen, BLACK, (350, 100), (350, 150), 8)

    if turns < 6:
        # Head
        pygame.draw.circle(screen, BLACK, (350, 180), 30, 8)
    if turns < 5:
        # Body
        pygame.draw.line(screen, BLACK, (350, 210), (350, 300), 8)
    if turns < 4:
        # Left arm
        pygame.draw.line(screen, BLACK, (350, 230), (300, 260), 8)
    if turns < 3:
        # Right arm
        pygame.draw.line(screen, BLACK, (350, 230), (400, 260), 8)
    if turns < 2:
        # Left leg
        pygame.draw.line(screen, BLACK, (350, 300), (300, 350), 8)
    if turns < 1:
        # Right leg
        pygame.draw.line(screen, BLACK, (350, 300), (400, 350), 8)

def display_word(word, guesses):
    display = ""
    for letter in word:
        if letter in guesses:
            display += letter + " "
        else:
            display += "_ "
    return display.strip()

def draw_input_box(rect, text, active, cursor_visible):
    color = LIGHT_BLUE if active else GRAY
    pygame.draw.rect(screen, color, rect, 2)
    text_surface = FONT.render(text, True, BLACK)
    screen.blit(text_surface, (rect.x + 5, rect.y + 5))
    if active and cursor_visible:
        cursor_pos = rect.x + 5 + text_surface.get_width()
        pygame.draw.line(screen, BLACK, (cursor_pos, rect.y + 5), (cursor_pos, rect.y + rect.height - 5), 2)

def title_screen():
    name = ""
    age = ""
    input_name = True
    input_age = False

    name_box = pygame.Rect(WIDTH // 2 - 100, 240, 200, 32)
    age_box = pygame.Rect(WIDTH // 2 - 100, 340, 200, 32)

    cursor_visible = True
    last_cursor_toggle = time.time()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if input_name:
                        input_name = False
                        input_age = True
                    elif input_age:
                        try:
                            age = int(age)
                            return name, age
                        except ValueError:
                            age = ""
                elif event.key == pygame.K_BACKSPACE:
                    if input_name:
                        name = name[:-1]
                    elif input_age:
                        age = age[:-1]
                else:
                    if input_name:
                        name += event.unicode
                    elif input_age and event.unicode.isdigit():
                        age += event.unicode

        screen.fill(WHITE)
        title = LARGE_FONT.render("Hangman", True, BLUE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        name_prompt = FONT.render("Enter your name:", True, BLACK)
        screen.blit(name_prompt, (WIDTH // 2 - name_prompt.get_width() // 2, 200))
        draw_input_box(name_box, name, input_name, cursor_visible)

        age_prompt = FONT.render("Enter your age:", True, BLACK)
        screen.blit(age_prompt, (WIDTH // 2 - age_prompt.get_width() // 2, 300))
        draw_input_box(age_box, age, input_age, cursor_visible)

        # Add instruction text
        instruction = SMALL_FONT.render("Press Enter to confirm and move to the next field", True, BLACK)
        screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, 400))

        # Toggle cursor visibility every 0.5 seconds
        if time.time() - last_cursor_toggle > 0.5:
            cursor_visible = not cursor_visible
            last_cursor_toggle = time.time()

        pygame.display.flip()

def play_again_screen():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                elif event.key == pygame.K_n:
                    return False

        screen.fill(WHITE)
        play_again_text = LARGE_FONT.render("Play Again?", True, BLUE)
        screen.blit(play_again_text, (WIDTH // 2 - play_again_text.get_width() // 2, HEIGHT // 2 - 100))
        
        yes_text = FONT.render("Press 'Y' for Yes", True, GREEN)
        screen.blit(yes_text, (WIDTH // 2 - yes_text.get_width() // 2, HEIGHT // 2))
        
        no_text = FONT.render("Press 'N' for No", True, RED)
        screen.blit(no_text, (WIDTH // 2 - no_text.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.flip()

def hangman(name, age):
    word = get_word(age).upper()
    guesses = set()
    turns = 20

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key >= pygame.K_a and event.key <= pygame.K_z:
                    guess = chr(event.key).upper()
                    if guess not in guesses:
                        guesses.add(guess)
                        if guess not in word:
                            turns -= 1

        screen.fill(LIGHT_BLUE)

        # Draw hangman
        draw_hangman(turns)

        # Display word
        word_display = FONT.render(display_word(word, guesses), True, BLACK)
        screen.blit(word_display, (400, 400))

        # Display guessed letters
        guessed_letters = FONT.render("Guessed: " + " ".join(sorted(guesses)), True, BLACK)
        screen.blit(guessed_letters, (400, 450))

        # Display turns left
        turns_text = FONT.render(f"Turns left: {turns}", True, BLACK)
        screen.blit(turns_text, (400, 500))

        # Display player name
        name_text = FONT.render(f"Player: {name}", True, BLUE)
        screen.blit(name_text, (20, 20))

        # Check for win/lose conditions
        if set(word) <= guesses:
            win_text = LARGE_FONT.render("You Won!", True, GREEN)
            screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, 50))
            pygame.display.flip()
            pygame.time.wait(2000)
            return play_again_screen()
        elif turns == 0:
            lose_text = LARGE_FONT.render("You Lost!", True, RED)
            screen.blit(lose_text, (WIDTH // 2 - lose_text.get_width() // 2, 50))
            word_reveal = FONT.render(f"The word was: {word}", True, BLACK)
            screen.blit(word_reveal, (WIDTH // 2 - word_reveal.get_width() // 2, 120))
            pygame.display.flip()
            pygame.time.wait(2000)
            return play_again_screen()

        pygame.display.flip()

if __name__ == "__main__":
    while True:
        name, age = title_screen()
        play_again = True
        while play_again:
            play_again = hangman(name, age)
