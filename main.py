import pygame
import random
import sys
import math
import struct

# Pygame & Mixer Initialize for Procedural Sound
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=1)

# Full Vertical Screen Auto-Detection for Mobile
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
if WIDTH > HEIGHT: # Safety fallback if launched in landscape
    WIDTH, HEIGHT = 480, 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Retro Neon Hangman - 50 Levels")

# Retro Neon Yellow & Dark Cyber Palette
BG_COLOR = (12, 10, 2)          # Deep Retro Dark Amber
NEON_YELLOW = (255, 230, 0)     # Glowing Neon Yellow
NEON_ORANGE = (255, 130, 0)     # Neon Orange Accent
NEON_GREEN = (0, 255, 120)      # Neon Success Green
NEON_RED = (255, 40, 60)        # Neon Danger Red
PANEL_COLOR = (28, 22, 5)       # Retro Box Fill
TEXT_WHITE = (255, 255, 255)
DIM_GRAY = (80, 70, 50)

# Scaled Fonts for Full Vertical Screen
FONT_S = pygame.font.SysFont(None, int(HEIGHT * 0.025))
FONT_M = pygame.font.SysFont(None, int(HEIGHT * 0.035))
FONT_L = pygame.font.SysFont(None, int(HEIGHT * 0.045))
FONT_XL = pygame.font.SysFont(None, int(HEIGHT * 0.06))

# --- PROCEDURAL RETRO SOUND GENERATOR ---
def create_sound(freq_start, freq_end, duration, sound_type="square"):
    sample_rate = 22050
    n_samples = int(sample_rate * duration)
    buffer = bytearray()
    for i in range(n_samples):
        t = i / sample_rate
        freq = freq_start + (freq_end - freq_start) * (i / n_samples)
        if sound_type == "square":
            val = 16383 if math.sin(2 * math.pi * freq * t) > 0 else -16383
        else:
            val = int(16383 * math.sin(2 * math.pi * freq * t))
        buffer.extend(struct.pack('<h', int(val * 0.4)))
    return pygame.mixer.Sound(buffer=bytes(buffer))

# Sound FX
tap_snd = create_sound(700, 700, 0.04, "square")
win_snd = create_sound(440, 880, 0.35, "sine")
lose_snd = create_sound(220, 110, 0.4, "square")

# --- EXPANDED 8-9+ LETTER WORDS & HINTS DICTIONARY ---
WORD_HINTS = {
    # Level 1-10: Easy Long Words (8-9 letters)
    "PLAYGROUND": "Area for children to play outdoors",
    "BOOKSHELF": "Furniture to keep books",
    "BACKPACKS": "Bags worn on shoulders",
    "SUNSHINE": "Light and heat from the sun",
    "CHOCOLATE": "Sweet brown edible treat",
    "NOTEBOOK": "Book for writing notes",
    "AIRPLANE": "Flying vehicle with wings",
    "BASEBALL": "Bat and glove team sport",
    "RAINBOWS": "Colorful arcs in the sky",
    "FIREFLIES": "Insects that glow in dark",

    # Level 11-25: Medium Long Words (8-10 letters)
    "LABYRINTH": "A complex maze puzzle",
    "SYMPHONY": "Large orchestra musical composition",
    "TELESCOPE": "Tool to see distant stars",
    "ASTRONOMY": "Study of space and stars",
    "DICTIONARY": "Book containing word meanings",
    "ACCELERATE": "To increase speed rapidly",
    "EXPERIMENT": "Scientific test in lab",
    "ATMOSPHERE": "Layer of gases around Earth",
    "FOUNDATION": "The solid base of a building",
    "NAVIGATION": "Guiding a vehicle or journey",

    # Level 26-40: Hard Technical Words (9-11 letters)
    "CARTOGRAPHY": "The science of making maps",
    "DOCUMENTARY": "Non-fiction educational film",
    "ELECTRICITY": "Flow of electric power",
    "ILLUMINATE": "To light up or brighten",
    "OBSERVATORY": "Building for stargazing",
    "SEISMOLOGY": "Study of earthquakes",
    "ARCHITECTURAL": "Relating to building design",
    "BIOCHEMISTRY": "Chemistry of living things",
    "CYBERNETICS": "Control systems in machines",
    "THERMODYNAMIC": "Relating to heat and energy",

    # Level 41-50: Expert Extreme Words (10-15+ letters)
    "CRYPTOGRAPHY": "Secure secret coding systems",
    "MICROCONTROLLER": "Small embedded computer chip",
    "NEURALNETWORK": "AI brain simulation model",
    "SUPERCOMPUTER": "Extremely fast high-end computer",
    "QUANTUMCOMPUTING": "Next-gen physics computing",
    "BIOINFORMATICS": "Biology data analysis",
    "NANOTECHNOLOGY": "Engineering at atomic scale",
    "ELECTROMAGNETIC": "Relating to magnetic fields",
    "SYNTHETICALLY": "Made artificially in lab",
    "CYBERSECURITY": "Protecting digital systems"
}

def get_word(level):
    if level <= 10:
        words = ["PLAYGROUND", "BOOKSHELF", "BACKPACKS", "SUNSHINE", "CHOCOLATE", "NOTEBOOK", "AIRPLANE", "BASEBALL", "RAINBOWS", "FIREFLIES"]
    elif level <= 25:
        words = ["LABYRINTH", "SYMPHONY", "TELESCOPE", "ASTRONOMY", "DICTIONARY", "ACCELERATE", "EXPERIMENT", "ATMOSPHERE", "FOUNDATION", "NAVIGATION"]
    elif level <= 40:
        words = ["CARTOGRAPHY", "DOCUMENTARY", "ELECTRICITY", "ILLUMINATE", "OBSERVATORY", "SEISMOLOGY", "ARCHITECTURAL", "BIOCHEMISTRY", "CYBERNETICS", "THERMODYNAMIC"]
    else:
        words = ["CRYPTOGRAPHY", "MICROCONTROLLER", "NEURALNETWORK", "SUPERCOMPUTER", "QUANTUMCOMPUTING", "BIOINFORMATICS", "NANOTECHNOLOGY", "ELECTROMAGNETIC", "SYNTHETICALLY", "CYBERSECURITY"]
    return random.choice(words)

def draw_neon_hangman(errors, w, h):
    cx = w // 2
    base_y = int(h * 0.36)
    pole_x = cx - int(w * 0.18)
    beam_x = cx + int(w * 0.04)
    
    # Retro Gallows
    pygame.draw.line(screen, NEON_ORANGE, (pole_x - 40, base_y), (pole_x + 50, base_y), 6)
    pygame.draw.line(screen, NEON_ORANGE, (pole_x, int(h * 0.10)), (pole_x, base_y), 6)
    pygame.draw.line(screen, NEON_ORANGE, (pole_x, int(h * 0.10)), (beam_x, int(h * 0.10)), 6)
    pygame.draw.line(screen, NEON_YELLOW, (beam_x - 15, int(h * 0.10)), (beam_x - 15, int(h * 0.10) + 25), 4)

    head_center = (beam_x - 15, int(h * 0.10) + 45)
    head_radius = int(w * 0.045)
    body_top_y = head_center[1] + head_radius
    body_bottom_y = body_top_y + int(h * 0.10)

    # Stickman Body Parts
    if errors >= 1: # Head
        pygame.draw.circle(screen, NEON_RED, head_center, head_radius, 4)
    if errors >= 2: # Body
        pygame.draw.line(screen, NEON_RED, (head_center[0], body_top_y), (head_center[0], body_bottom_y), 4)
    if errors >= 3: # Left Arm
        pygame.draw.line(screen, NEON_RED, (head_center[0], body_top_y + 15), (head_center[0] - 35, body_top_y + 45), 4)
    if errors >= 4: # Right Arm
        pygame.draw.line(screen, NEON_RED, (head_center[0], body_top_y + 15), (head_center[0] + 35, body_top_y + 45), 4)
    if errors >= 5: # Left Leg
        pygame.draw.line(screen, NEON_RED, (head_center[0], body_bottom_y), (head_center[0] - 30, body_bottom_y + 55), 4)
    if errors >= 6: # Right Leg
        pygame.draw.line(screen, NEON_RED, (head_center[0], body_bottom_y), (head_center[0] + 30, body_bottom_y + 55), 4)

def get_keyboard_layout(width, height):
    rows = [
        ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
        ["Z", "X", "C", "V", "B", "N", "M"]
    ]
    buttons = {}
    button_w = int(width * 0.088)
    button_h = int(height * 0.062)
    spacing = int(width * 0.012)
    start_y = int(height * 0.63)

    for r_idx, row in enumerate(rows):
        row_w = len(row) * (button_w + spacing) - spacing
        start_x = (width - row_w) // 2
        for c_idx, letter in enumerate(row):
            bx = start_x + c_idx * (button_w + spacing)
            by = start_y + r_idx * (button_h + spacing)
            buttons[letter] = pygame.Rect(bx, by, button_w, button_h)
    return buttons

def game_loop():
    level = 1
    score = 0
    keyboard_buttons = get_keyboard_layout(WIDTH, HEIGHT)
    hint_btn_rect = pygame.Rect(WIDTH//2 - 90, int(HEIGHT * 0.54), 180, 42)
    
    while level <= 50:
        word = get_word(level)
        guessed = set()
        
        # Pre-fill one unique letter automatically (Head Start)
        unique_letters = list(set(word))
        pre_fill_letter = random.choice(unique_letters)
        guessed.add(pre_fill_letter)

        errors = 0
        max_errors = 6
        hint_used = False
        show_hint_text = False
        clock = pygame.time.Clock()
        
        running = True
        while running:
            screen.fill(BG_COLOR)
            
            # Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    
                    # Hint Button Click
                    if hint_btn_rect.collidepoint(pos):
                        if not hint_used:
                            tap_snd.play()
                            hint_used = True
                            show_hint_text = True
                    
                    # Keyboard Letters Click
                    for letter, rect in keyboard_buttons.items():
                        if rect.collidepoint(pos):
                            if letter not in guessed:
                                tap_snd.play()
                                guessed.add(letter)
                                if letter not in word:
                                    errors += 1

            # --- HEADER ---
            lvl_surf = FONT_L.render(f"LEVEL {level} / 50", True, NEON_YELLOW)
            score_surf = FONT_M.render(f"SCORE: {score}", True, NEON_ORANGE)
            screen.blit(lvl_surf, (25, 20))
            screen.blit(score_surf, (WIDTH - score_surf.get_width() - 25, 25))

            pygame.draw.line(screen, NEON_YELLOW, (20, 65), (WIDTH - 20, 65), 2)

            # --- HANGMAN DRAWING ---
            draw_neon_hangman(errors, WIDTH, HEIGHT)

            # --- WORD BLANKS DISPLAY (Adjusted font size for long words) ---
            display_word = " ".join([letter if letter in guessed else "_" for letter in word])
            # Dynamic scaling if word is very long
            word_font = FONT_XL if len(word) <= 10 else pygame.font.SysFont(None, int(HEIGHT * 0.045))
            word_surf = word_font.render(display_word, True, NEON_YELLOW)
            screen.blit(word_surf, (WIDTH//2 - word_surf.get_width()//2, int(HEIGHT * 0.40)))

            # --- HINT BUTTON & DISPLAY ---
            pygame.draw.rect(screen, (35, 30, 10), hint_btn_rect, border_radius=6)
            pygame.draw.rect(screen, NEON_ORANGE, hint_btn_rect, 2, border_radius=6)
            hint_lbl = FONT_S.render("💡 GET HINT" if not hint_used else "💡 HINT USED", True, NEON_ORANGE if not hint_used else DIM_GRAY)
            screen.blit(hint_lbl, (hint_btn_rect.centerx - hint_lbl.get_width()//2, hint_btn_rect.centery - hint_lbl.get_height()//2))

            if show_hint_text:
                hint_desc = WORD_HINTS.get(word, "Think carefully!")
                desc_surf = FONT_S.render(f"Hint: {hint_desc}", True, TEXT_WHITE)
                screen.blit(desc_surf, (WIDTH//2 - desc_surf.get_width()//2, int(HEIGHT * 0.49)))

            # --- ON-SCREEN RETRO KEYBOARD WITH RED CROSS ---
            for letter, rect in keyboard_buttons.items():
                is_guessed = letter in guessed
                is_wrong = is_guessed and (letter not in word)
                
                box_color = PANEL_COLOR
                border_color = NEON_YELLOW
                text_color = NEON_YELLOW
                
                if is_guessed:
                    if is_wrong:
                        box_color = (45, 10, 15)
                        border_color = NEON_RED
                        text_color = NEON_RED
                    else:
                        box_color = (10, 45, 25)
                        border_color = NEON_GREEN
                        text_color = NEON_GREEN

                pygame.draw.rect(screen, box_color, rect, border_radius=6)
                pygame.draw.rect(screen, border_color, rect, 2, border_radius=6)
                
                l_surf = FONT_M.render(letter, True, text_color)
                screen.blit(l_surf, (rect.centerx - l_surf.get_width()//2, rect.centery - l_surf.get_height()//2))
                
                if is_wrong:
                    pygame.draw.line(screen, NEON_RED, (rect.left + 5, rect.top + 5), (rect.right - 5, rect.bottom - 5), 3)
                    pygame.draw.line(screen, NEON_RED, (rect.left + 5, rect.bottom - 5), (rect.right - 5, rect.top + 5), 3)

            # --- CHECK WIN CONDITION ---
            if all(letter in guessed for letter in word):
                win_snd.play()
                score += 35 + (max_errors - errors) * 8
                
                # Celebration Animation Loop
                particles = [[random.randint(50, WIDTH-50), random.randint(100, HEIGHT-100), random.choice([NEON_GREEN, NEON_YELLOW, NEON_ORANGE])] for _ in range(35)]
                celebrate_timer = 0
                while celebrate_timer < 45:
                    screen.fill(BG_COLOR)
                    for p in particles:
                        p[1] -= 4
                        pygame.draw.circle(screen, p[2], (p[0], p[1]), 5)
                    
                    win_text = FONT_XL.render("⚡ LEVEL CLEARED! ⚡", True, NEON_GREEN)
                    next_text = FONT_M.render("Tap anywhere for Next Level", True, TEXT_WHITE)
                    screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - 40))
                    screen.blit(next_text, (WIDTH//2 - next_text.get_width()//2, HEIGHT//2 + 30))
                    pygame.display.flip()
                    
                    for e in pygame.event.get():
                        if e.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                    clock.tick(30)
                    celebrate_timer += 1
                
                waiting = True
                while waiting:
                    for e in pygame.event.get():
                        if e.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if e.type == pygame.MOUSEBUTTONDOWN:
                            tap_snd.play()
                            waiting = False
                level += 1
                running = False

            # --- CHECK LOSS CONDITION ---
            elif errors >= max_errors:
                lose_snd.play()
                screen.fill(BG_COLOR)
                draw_neon_hangman(max_errors, WIDTH, HEIGHT)
                loss_text = FONT_XL.render("💀 GAME OVER 💀", True, NEON_RED)
                ans_text = FONT_L.render(f"Word was: {word}", True, NEON_YELLOW)
                retry_text = FONT_S.render("Tap anywhere to Retry Level", True, NEON_ORANGE)
                
                screen.blit(loss_text, (WIDTH//2 - loss_text.get_width()//2, int(HEIGHT * 0.42)))
                screen.blit(ans_text, (WIDTH//2 - ans_text.get_width()//2, int(HEIGHT * 0.50)))
                screen.blit(retry_text, (WIDTH//2 - retry_text.get_width()//2, int(HEIGHT * 0.58)))
                pygame.display.flip()
                
                waiting = True
                while waiting:
                    for e in pygame.event.get():
                        if e.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if e.type == pygame.MOUSEBUTTONDOWN:
                            tap_snd.play()
                            waiting = False
                running = False

            pygame.display.flip()
            clock.tick(30)

    # Final Victory Screen
    screen.fill(BG_COLOR)
    fin_text = FONT_L.render("🏆 YOU BEAT ALL 50 LEVELS! 🏆", True, NEON_GREEN)
    final_score_txt = FONT_M.render(f"Final Neon Score: {score}", True, NEON_YELLOW)
    screen.blit(fin_text, (WIDTH//2 - fin_text.get_width()//2, HEIGHT//2 - 40))
    screen.blit(final_score_txt, (WIDTH//2 - final_score_txt.get_width()//2, HEIGHT//2 + 15))
    pygame.display.flip()
    
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

if __name__ == "__main__":
    game_loop()
