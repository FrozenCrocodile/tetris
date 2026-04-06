import pygame
import random
import os

# Initialize pygame
pygame.init()
pygame.mixer.init()

try:
    base_path = os.path.dirname(os.path.abspath(__file__))
    move_sound = pygame.mixer.Sound(os.path.join(base_path, 'move.wav'))
    rotate_sound = pygame.mixer.Sound(os.path.join(base_path, 'rotate.wav'))
    drop_sound = pygame.mixer.Sound(os.path.join(base_path, 'drop.wav'))
    clear_sound = pygame.mixer.Sound(os.path.join(base_path, 'clear.wav'))
    gameover_sound = pygame.mixer.Sound(os.path.join(base_path, 'gameover.wav'))
except Exception as e:
    print(f"Error loading sounds: {e}")
    move_sound = rotate_sound = drop_sound = clear_sound = gameover_sound = None

sound_enabled = True

def play_sound(sound):
    global sound_enabled
    if sound and sound_enabled:
        sound.play()

# Screen dimensions
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 850
PLAY_WIDTH = 300   # meaning 300 // 10 = 30 width per block
PLAY_HEIGHT = 600  # meaning 600 // 20 = 30 height per block
BLOCK_SIZE = 30

top_left_x = (SCREEN_WIDTH - PLAY_WIDTH) // 2
top_left_y = 150

# Shapes formats

S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]
# index 0 - 6 represent shape

class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0

class Button:
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, win, outline=None):
        if outline:
            pygame.draw.rect(win, outline, (self.x-2, self.y-2, self.width+4, self.height+4), 0)
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)
        
        if self.text != '':
            try:
                font = pygame.font.SysFont('comicsans', 18, bold=True)
            except:
                font = pygame.font.Font(pygame.font.get_default_font(), 18)
            text_rend = font.render(self.text, 1, (0,0,0))
            win.blit(text_rend, (self.x + (self.width/2 - text_rend.get_width()/2), self.y + (self.height/2 - text_rend.get_height()/2)))

    def is_over(self, pos):
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
        return False

# Buttons
btn_left = Button((200, 200, 200), 20, 770, 100, 60, "Left")
btn_rotate = Button((200, 200, 200), 140, 770, 100, 60, "Rotate")
btn_drop = Button((200, 200, 200), 260, 770, 100, 60, "Drop")
btn_right = Button((200, 200, 200), 380, 770, 100, 60, "Right")
btn_pause = Button((200, 200, 200), 10, 10, 80, 40, "Pause")
btn_mute = Button((200, 200, 200), 100, 10, 80, 40, "Mute")
btn_exit = Button((200, 200, 200), 410, 10, 80, 40, "Exit")
buttons = [btn_left, btn_rotate, btn_drop, btn_right, btn_pause, btn_mute, btn_exit]

def create_grid(locked_pos={}):
    grid = [[(0,0,0) for _ in range(10)] for _ in range(20)]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_pos:
                c = locked_pos[(j,i)]
                grid[i][j] = c
    return grid

def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))
    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)
    return positions

def valid_space(shape, grid):
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]
    formatted = convert_shape_format(shape)
    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def get_shape():
    return Piece(5, 0, random.choice(shapes))

def get_high_score_data():
    if not os.path.exists('scores.txt'):
        with open('scores.txt', 'w') as f:
            f.write('0')
    name, score = "", 0
    with open('scores.txt', 'r') as f:
        lines = f.readlines()
        if len(lines) > 0:
            content = lines[0].strip()
            if ',' in content:
                parts = content.rsplit(',', 1)
                name, score_str = parts[0], parts[1]
                if score_str.isdigit():
                    score = int(score_str)
            elif content.isdigit():
                score = int(content)
    return name, score

def get_high_score_display():
    name, score = get_high_score_data()
    if name:
        return f"{name}: {score}"
    return str(score)

def enter_name_screen(win):
    run = True
    name = ""
    font = pygame.font.SysFont('comicsans', 40)
    font2 = pygame.font.SysFont('comicsans', 30)
    while run:
        win.fill((0,0,0))
        label1 = font.render("NEW HIGH SCORE!", 1, (255, 255, 0))
        label2 = font2.render("Enter Name: " + name + "_", 1, (255, 255, 255))
        
        cx = top_left_x + PLAY_WIDTH / 2
        cy = top_left_y + PLAY_HEIGHT / 2
        win.blit(label1, (cx - label1.get_width() / 2, cy - 50))
        win.blit(label2, (cx - label2.get_width() / 2, cy + 10))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return name.strip()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 15 and event.unicode.isprintable():
                        name += event.unicode
    return name.strip()

def draw_text_middle(surface, text, size, color):
    # Fallback font handling
    try:
        font = pygame.font.SysFont("comicsans", size, bold=True)
    except:
        font = pygame.font.Font(pygame.font.get_default_font(), size)
    label = font.render(text, 1, color)
    surface.blit(label, (top_left_x + PLAY_WIDTH /2 - (label.get_width()/2), top_left_y + PLAY_HEIGHT/2 - label.get_height()/2))

def draw_grid(surface, grid):
    for i in range(len(grid)):
        pygame.draw.line(surface, (128,128,128), (top_left_x, top_left_y + i*BLOCK_SIZE), (top_left_x+PLAY_WIDTH, top_left_y+ i*BLOCK_SIZE))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128), (top_left_x + j*BLOCK_SIZE, top_left_y), (top_left_x + j*BLOCK_SIZE, top_left_y + PLAY_HEIGHT))

def clear_rows(grid, locked):
    cleared_rows = []
    for i in range(len(grid)):
        if (0,0,0) not in grid[i]:
            cleared_rows.append(i)
            
    if cleared_rows:
        for i in cleared_rows:
            for j in range(len(grid[i])):
                if (j, i) in locked:
                    del locked[(j, i)]
                    
        new_locked = {}
        for (x, y), color in locked.items():
            shift = sum(1 for row_idx in cleared_rows if row_idx > y)
            new_locked[(x, y + shift)] = color
            
        locked.clear()
        locked.update(new_locked)
        
    return len(cleared_rows)

def draw_next_shape(shape, surface):
    try:
        font = pygame.font.SysFont('comicsans', 20)
    except:
        font = pygame.font.Font(pygame.font.get_default_font(), 20)
    label = font.render('Next Shape', 1, (255,255,255))
    
    sx = top_left_x + PLAY_WIDTH + 10
    sy = top_left_y + PLAY_HEIGHT/2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    surface.blit(label, (sx, sy - 30))
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j*20, sy + i*20, 20, 20), 0)

def draw_window(surface, grid, score=0, last_score=0, lines_cleared=0, next_piece=None):
    surface.fill((0, 0, 0))
    pygame.font.init()
    try:
        font = pygame.font.SysFont('comicsans', 40)
    except:
        font = pygame.font.Font(pygame.font.get_default_font(), 40)
    
    label = font.render('Tetris', 1, (255, 255, 255))
    surface.blit(label, (SCREEN_WIDTH / 2 - (label.get_width() / 2), 20))
    
    try:
        font2 = pygame.font.SysFont('comicsans', 20)
    except:
        font2 = pygame.font.Font(pygame.font.get_default_font(), 20)
    
    label2 = font2.render('Score: ' + str(score), 1, (255,255,255))
    surface.blit(label2, (SCREEN_WIDTH / 2 - (label2.get_width() / 2), 65))

    label_high = font2.render('High Score: ' + str(last_score), 1, (255,255,255))
    surface.blit(label_high, (SCREEN_WIDTH / 2 - (label_high.get_width() / 2), 90))

    label_lines = font2.render('Lines: ' + str(lines_cleared), 1, (255,255,255))
    surface.blit(label_lines, (SCREEN_WIDTH / 2 - (label_lines.get_width() / 2), 115))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j*BLOCK_SIZE, top_left_y + i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, PLAY_WIDTH, PLAY_HEIGHT), 5)
    draw_grid(surface, grid)

    for btn in buttons:
        btn.draw(surface, (255, 255, 255))

    if next_piece:
        draw_next_shape(next_piece, surface)

    pygame.display.update()

def main(win):
    global sound_enabled
    locked_positions = {}
    grid = create_grid(locked_positions)
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5
    level_time = 0
    score = 0
    last_score = get_high_score_display()
    lines_cleared_count = 0
    paused = False

    while run:
        if not paused:
            grid = create_grid(locked_positions)
            fall_time += clock.get_rawtime()
            level_time += clock.get_rawtime()
            clock.tick()

            if level_time/1000 > 5:
                level_time = 0
                if fall_speed > 0.12:
                    fall_speed -= 0.002

            if fall_time/1000 > fall_speed:
                fall_time = 0
                current_piece.y += 1
                if not(valid_space(current_piece, grid)) and current_piece.y > 0:
                    current_piece.y -= 1
                    change_piece = True
        else:
            clock.tick()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                    btn_pause.text = "Resume" if paused else "Pause"
                if not paused:
                    if event.key == pygame.K_LEFT:
                        current_piece.x -= 1
                        if not(valid_space(current_piece, grid)):
                            current_piece.x += 1
                        else:
                            play_sound(move_sound)
                    if event.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not(valid_space(current_piece, grid)):
                            current_piece.x -= 1
                        else:
                            play_sound(move_sound)
                    if event.key == pygame.K_DOWN:
                        current_piece.y += 1
                        if not(valid_space(current_piece, grid)):
                            current_piece.y -= 1
                        else:
                            play_sound(move_sound)
                    if event.key == pygame.K_UP:
                        current_piece.rotation += 1
                        if not(valid_space(current_piece, grid)):
                            current_piece.rotation -= 1
                        else:
                            play_sound(rotate_sound)
                    if event.key == pygame.K_SPACE:
                        while valid_space(current_piece, grid):
                            current_piece.y += 1
                        current_piece.y -= 1
                        play_sound(drop_sound)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = pygame.mouse.get_pos()
                    if btn_exit.is_over(pos):
                        run = False
                        return False
                    elif btn_pause.is_over(pos):
                        paused = not paused
                        btn_pause.text = "Resume" if paused else "Pause"
                    elif btn_mute.is_over(pos):
                        sound_enabled = not sound_enabled
                        btn_mute.text = "Unmute" if not sound_enabled else "Mute"
                    elif not paused:
                        if btn_left.is_over(pos):
                            current_piece.x -= 1
                            if not(valid_space(current_piece, grid)):
                                current_piece.x += 1
                            else:
                                play_sound(move_sound)
                        elif btn_right.is_over(pos):
                            current_piece.x += 1
                            if not(valid_space(current_piece, grid)):
                                current_piece.x -= 1
                            else:
                                play_sound(move_sound)
                        elif btn_rotate.is_over(pos):
                            current_piece.rotation += 1
                            if not(valid_space(current_piece, grid)):
                                current_piece.rotation -= 1
                            else:
                                play_sound(rotate_sound)
                        elif btn_drop.is_over(pos):
                            while valid_space(current_piece, grid):
                                current_piece.y += 1
                            current_piece.y -= 1
                            play_sound(drop_sound)

        if not paused:
            shape_pos = convert_shape_format(current_piece)
            for i in range(len(shape_pos)):
                x, y = shape_pos[i]
                if y > -1:
                    grid[y][x] = current_piece.color

            if change_piece:
                for pos in shape_pos:
                    p = (pos[0], pos[1])
                    locked_positions[p] = current_piece.color
                current_piece = next_piece
                next_piece = get_shape()
                change_piece = False
                cleared = clear_rows(grid, locked_positions)
                if cleared == 1:
                    score += 10
                elif cleared == 2:
                    score += 30
                elif cleared == 3:
                    score += 50
                elif cleared >= 4:
                    score += 80
                lines_cleared_count += cleared
                if cleared > 0:
                    play_sound(clear_sound)

        draw_window(win, grid, score, last_score, lines_cleared_count, next_piece)

        if paused:
            draw_text_middle(win, "PAUSED", 80, (255,255,255))
            pygame.display.update()

        if check_lost(locked_positions):
            play_sound(gameover_sound)
            draw_text_middle(win, "YOU LOST!", 80, (255,255,255))
            pygame.display.update()
            pygame.time.delay(2000)
            
            _, current_hs = get_high_score_data()
            if score > current_hs:
                new_name = enter_name_screen(win)
                if not new_name:
                    new_name = "Anonymous"
                with open('scores.txt', 'w') as f:
                    f.write(f"{new_name},{score}")
                    
            run = False

def main_menu(win):
    run = True
    while run:
        win.fill((0,0,0))
        draw_text_middle(win, "Press Any Key To Play", 30, (255,255,255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                res = main(win)
                if res is False:
                    run = False
    pygame.display.quit()
    pygame.quit()

if __name__ == '__main__':
    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Tetris')
    main_menu(win)
