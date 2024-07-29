import pygame
import random
import json
import os

pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# Game dimensions
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
PLAY_WIDTH = BLOCK_SIZE * GRID_WIDTH
PLAY_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
SIDEBAR_WIDTH = 200
INSTRUCTIONS_WIDTH = 300
SCREEN_WIDTH = PLAY_WIDTH + SIDEBAR_WIDTH * 2 + INSTRUCTIONS_WIDTH
SCREEN_HEIGHT = max(PLAY_HEIGHT, 720)  # Ensure a minimum height

PREVIEW_SIZE = 4
PREVIEW_OFFSET_X = PLAY_WIDTH + SIDEBAR_WIDTH + 20
PREVIEW_OFFSET_Y = 50

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]]
]

COLORS = [CYAN, YELLOW, MAGENTA, RED, GREEN, BLUE, ORANGE]

CUSTOM_COLORS = {
    'cyan': CYAN, 'yellow': YELLOW, 'magenta': MAGENTA,
    'red': RED, 'green': GREEN, 'blue': BLUE, 'orange': ORANGE
}

DEFAULT_SPEED = 5

class Tetromino:
    def __init__(self, shape=None):
        self.shape = shape or random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0
        self.rotation = 0

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def rotate(self):
        self.shape = list(zip(*self.shape[::-1]))
        self.rotation = (self.rotation + 1) % 4

    def undo_rotate(self):
        for _ in range(3):
            self.rotate()

class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.load_settings()
        self.load_high_scores()
        self.reset_game()
        self.fullscreen = False

    def reset_game(self):
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.bag = self.generate_bag()
        self.current_piece = self.get_next_piece()
        self.next_pieces = [self.get_next_piece() for _ in range(3)]
        self.hold_piece = None
        self.can_hold = True
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.paused = False
        self.combo = 0
        self.last_move_was_tetris = False
        self.show_ghost = True
        self.show_instructions = True

    def generate_bag(self):
        bag = list(range(len(SHAPES)))
        random.shuffle(bag)
        return bag

    def get_next_piece(self):
        if not self.bag:
            self.bag = self.generate_bag()
        return Tetromino(SHAPES[self.bag.pop()])

    def load_settings(self):
        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as f:
                settings = json.load(f)
            self.custom_colors = settings.get('colors', list(CUSTOM_COLORS.values()))
            self.game_speed = settings.get('speed', DEFAULT_SPEED)
            self.show_ghost = settings.get('show_ghost', True)
        else:
            self.custom_colors = list(CUSTOM_COLORS.values())
            self.game_speed = DEFAULT_SPEED
            self.show_ghost = True

    def save_settings(self):
        settings = {
            'colors': self.custom_colors,
            'speed': self.game_speed,
            'show_ghost': self.show_ghost
        }
        with open('settings.json', 'w') as f:
            json.dump(settings, f)

    def load_high_scores(self):
        if os.path.exists('high_scores.json'):
            with open('high_scores.json', 'r') as f:
                self.high_scores = json.load(f)
        else:
            self.high_scores = []

    def save_high_scores(self):
        with open('high_scores.json', 'w') as f:
            json.dump(self.high_scores, f)

    def draw_grid(self):
        pygame.draw.rect(self.screen, WHITE, (SIDEBAR_WIDTH - 1, -1, PLAY_WIDTH + 2, PLAY_HEIGHT + 2), 2)
        
        for y, row in enumerate(self.grid):
            for x, color in enumerate(row):
                pygame.draw.rect(self.screen, color, 
                                 (SIDEBAR_WIDTH + x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
                pygame.draw.rect(self.screen, GRAY, 
                                 (SIDEBAR_WIDTH + x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

    def draw_piece(self, piece, offset_x=0, offset_y=0):
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, piece.color,
                                     (SIDEBAR_WIDTH + (piece.x + x + offset_x) * BLOCK_SIZE,
                                      (piece.y + y + offset_y) * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE), 0)

    def draw_ghost_piece(self):
        if not self.show_ghost:
            return
        ghost_piece = Tetromino(self.current_piece.shape)
        ghost_piece.x, ghost_piece.y = self.current_piece.x, self.current_piece.y
        while not self.check_collision(ghost_piece, 0, 1):
            ghost_piece.y += 1
        ghost_piece.y -= 1
        for y, row in enumerate(ghost_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, (*GRAY, 128),
                                     (SIDEBAR_WIDTH + (ghost_piece.x + x) * BLOCK_SIZE,
                                      (ghost_piece.y + y) * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE), 0)

    def draw_next_pieces(self):
        preview_text = self.font.render("Next:", True, WHITE)
        self.screen.blit(preview_text, (PREVIEW_OFFSET_X, 10))
        
        for i, piece in enumerate(self.next_pieces):
            for y, row in enumerate(piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, piece.color,
                                         (PREVIEW_OFFSET_X + x * BLOCK_SIZE,
                                          PREVIEW_OFFSET_Y + (i * 4 + y) * BLOCK_SIZE,
                                          BLOCK_SIZE, BLOCK_SIZE), 0)

    def draw_hold_piece(self):
        hold_text = self.font.render("Hold:", True, WHITE)
        self.screen.blit(hold_text, (10, 10))
        
        if self.hold_piece:
            for y, row in enumerate(self.hold_piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, self.hold_piece.color,
                                         (10 + x * BLOCK_SIZE,
                                          50 + y * BLOCK_SIZE,
                                          BLOCK_SIZE, BLOCK_SIZE), 0)

    def check_collision(self, piece, dx=0, dy=0):
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece.x + x + dx
                    new_y = piece.y + y + dy
                    if (new_x < 0 or new_x >= GRID_WIDTH or
                        new_y >= GRID_HEIGHT or
                        (new_y >= 0 and self.grid[new_y][new_x] != BLACK)):
                        return True
        return False

    def merge_piece(self):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece.y + y][self.current_piece.x + x] = self.current_piece.color

    def remove_full_rows(self):
        full_rows = [i for i, row in enumerate(self.grid) if all(cell != BLACK for cell in row)]
        for row in full_rows:
            del self.grid[row]
            self.grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
        
        lines_cleared = len(full_rows)
        self.lines_cleared += lines_cleared
        self.update_score(lines_cleared)
        
        self.level = self.lines_cleared // 10 + 1
        self.game_speed = min(DEFAULT_SPEED + self.level - 1, 20)

    def update_score(self, lines_cleared):
        line_scores = [100, 300, 500, 800]
        if lines_cleared > 0:
            score = line_scores[lines_cleared - 1] * self.level
            if lines_cleared == 4:
                if self.last_move_was_tetris:
                    score *= 1.5  # Back-to-back Tetris bonus
                self.last_move_was_tetris = True
            else:
                self.last_move_was_tetris = False
            
            self.combo += 1
            score += (50 * self.combo * self.level)  # Combo bonus
            
            self.score += int(score)
        else:
            self.combo = 0
            self.last_move_was_tetris = False

    def hard_drop(self):
        while not self.check_collision(self.current_piece, 0, 1):
            self.current_piece.move(0, 1)
        self.merge_piece()
        self.remove_full_rows()
        self.new_piece()

    def hold(self):
        if self.can_hold:
            if self.hold_piece:
                self.hold_piece, self.current_piece = self.current_piece, self.hold_piece
                self.current_piece.x = GRID_WIDTH // 2 - len(self.current_piece.shape[0]) // 2
                self.current_piece.y = 0
            else:
                self.hold_piece = self.current_piece
                self.new_piece()
            self.can_hold = False

    def new_piece(self):
        self.current_piece = self.next_pieces.pop(0)
        self.next_pieces.append(self.get_next_piece())
        if self.check_collision(self.current_piece):
            self.game_over = True
        self.can_hold = True

    def wall_kick(self, piece, rotation):
        kicks = [
            [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
            [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
            [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
            [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)]
        ]
        for dx, dy in kicks[rotation]:
            if not self.check_collision(piece, dx, dy):
                piece.x += dx
                piece.y += dy
                return True
        return False

    def draw_score_and_level(self):
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(score_text, (10, 150))
        self.screen.blit(level_text, (10, 190))

    def draw_game_over(self):
        game_over_font = pygame.font.Font(None, 64)
        game_over_text = game_over_font.render("GAME OVER", True, WHITE)
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        restart_text = self.font.render("Press ENTER for High Scores", True, WHITE)
        
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))

    def customize_colors(self):
        color_names = list(CUSTOM_COLORS.keys())
        current_color = 0
        selecting = True
        while selecting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        selecting = False
                    elif event.key == pygame.K_LEFT:
                        current_color = (current_color - 1) % len(color_names)
                    elif event.key == pygame.K_RIGHT:
                        current_color = (current_color + 1) % len(color_names)

            self.screen.fill(BLACK)
            text = self.font.render(f"Select color: {color_names[current_color]}", True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
            pygame.display.flip()

        self.custom_colors = [CUSTOM_COLORS[color_names[current_color]]] * 7
        self.save_settings()

    def draw_instructions(self):
        instructions = [
            "Left/Right: Move piece",
            "Down: Soft drop",
            "Up: Rotate piece",
            "Space: Hard drop",
            "C: Hold piece",
            "P: Pause game",
            "G: Toggle ghost piece",
            "+/-: Adjust speed",
            "R: Restart (when game over)",
            "F: Toggle full-screen"
        ]
        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH - INSTRUCTIONS_WIDTH + 10, 50 + i * 30))

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

    def handle_resize(self, event):
        if not self.fullscreen:
            new_width = max(event.w, SCREEN_WIDTH)
            new_height = max(event.h, SCREEN_HEIGHT)
            self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)

    def run(self):
        drop_time = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.VIDEORESIZE:
                    self.handle_resize(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        self.toggle_fullscreen()
                    elif event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif event.key == pygame.K_c:
                        self.customize_colors()
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.game_speed = min(self.game_speed + 1, 20)
                        self.save_settings()
                    elif event.key == pygame.K_MINUS:
                        self.game_speed = max(self.game_speed - 1, 1)
                        self.save_settings()
                    elif event.key == pygame.K_g:
                        self.show_ghost = not self.show_ghost
                        self.save_settings()
                    elif event.key == pygame.K_i:
                        self.show_instructions = not self.show_instructions
                    elif not self.paused and not self.game_over:
                        if event.key == pygame.K_LEFT:
                            if not self.check_collision(self.current_piece, -1, 0):
                                self.current_piece.move(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            if not self.check_collision(self.current_piece, 1, 0):
                                self.current_piece.move(1, 0)
                        elif event.key == pygame.K_DOWN:
                            if not self.check_collision(self.current_piece, 0, 1):
                                self.current_piece.move(0, 1)
                        elif event.key == pygame.K_UP:
                            self.current_piece.rotate()
                            if self.check_collision(self.current_piece):
                                if not self.wall_kick(self.current_piece, self.current_piece.rotation):
                                    self.current_piece.undo_rotate()
                        elif event.key == pygame.K_SPACE:
                            self.hard_drop()
                        elif event.key == pygame.K_c:
                            self.hold()
                    if event.key == pygame.K_r and self.game_over:
                        self.reset_game()

            if not self.paused and not self.game_over:
                drop_time += self.clock.get_rawtime()
                if drop_time > 1000 // self.game_speed:
                    if not self.check_collision(self.current_piece, 0, 1):
                        self.current_piece.move(0, 1)
                    else:
                        self.merge_piece()
                        self.remove_full_rows()
                        self.new_piece()
                    drop_time = 0

            self.screen.fill(BLACK)
            self.draw_grid()
            if self.show_ghost:
                self.draw_ghost_piece()
            self.draw_piece(self.current_piece)
            self.draw_next_pieces()
            self.draw_hold_piece()
            self.draw_score_and_level()

            if self.show_instructions:
                self.draw_instructions()

            if self.game_over:
                self.draw_game_over()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.update_high_scores()
                    while True:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                return
                            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                                self.reset_game()
                                break
                        else:
                            self.screen.fill(BLACK)
                            self.draw_high_scores()
                            pygame.display.flip()
                            continue
                        break
            elif self.paused:
                pause_text = self.font.render("PAUSED", True, WHITE)
                self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2))

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
