import pygame as pg
import json
from pygame.time import get_ticks
from enum import Enum

from constants import *
from enemy import Enemy
from world import World
from turret import Turret
from button import Button
from enemy_data import *


# Game state enumeration
class GameState(Enum):
    PLAYING = 0
    GAME_OVER = 1


pg.init()

# Clock
clock = pg.time.Clock()

# Create game window
screen = pg.display.set_mode((SCREEN_WIDTH + SIDE_PANEL, SCREEN_HEIGHT))
pg.display.set_caption("Tower Defence Game by Mateusz Majewski")

# Game variables
game_state = GameState.PLAYING
game_outcome = 0  # -1 = loss, 1 = win
level_started = False
placing_turrets = False
selected_turret = None
last_enemy_spawn = pg.time.get_ticks()

# Load images
# Map
map_image = pg.image.load('levels/level_1.png').convert_alpha()
# Turret spritesheets
turret_spritesheets = []
for x in range(1, TURRET_LEVELS + 1):
    turret_sheet = pg.image.load(f'assets/images/turrets/turret_01_mk{x}.png').convert_alpha()
    turret_spritesheets.append(turret_sheet)
# Turret for mouse cursor
cursor_turret = pg.image.load('assets/images/turrets/cursor_turret.png').convert_alpha()
# Enemies
enemy_images = {
    "weak": pg.image.load('assets/images/enemies/tank_1.png').convert_alpha(),
    "medium": pg.image.load('assets/images/enemies/tank_2.png').convert_alpha(),
    "strong": pg.image.load('assets/images/enemies/tank_3.png').convert_alpha(),
    "elite": pg.image.load('assets/images/enemies/tank_4.png').convert_alpha(),
    "boss_1": pg.image.load('assets/images/enemies/boss_1.png').convert_alpha(),
    "boss_2": pg.image.load('assets/images/enemies/boss_2.png').convert_alpha(),
    "boss_3": pg.image.load('assets/images/enemies/boss_3.png').convert_alpha(),
    "boss_4": pg.image.load('assets/images/enemies/boss_4.png').convert_alpha()
}
# Buttons
buy_turret_image = pg.image.load('assets/images/buttons/buy_turret_image.png').convert_alpha()
cancel_image = pg.image.load('assets/images/buttons/cancel_button_image.png').convert_alpha()
upgrade_turret_image = pg.image.load('assets/images/buttons/upgrade_button_image.png').convert_alpha()
begin_image = pg.image.load('assets/images/buttons/begin_button_image.png').convert_alpha()
fast_forward_image = pg.image.load('assets/images/buttons/fast_forward_button_image.png').convert_alpha()
restart_image = pg.image.load('assets/images/buttons/reset_button_image.png').convert_alpha()
continue_image = pg.image.load('assets/images/buttons/continue_button_image.png').convert_alpha()
play_button_image = pg.image.load(
    'assets/images/buttons/begin_button_image.png').convert_alpha()  # Reusing begin button for play
quit_button_image = pg.image.load(
    'assets/images/buttons/cancel_button_image.png').convert_alpha()  # Reusing cancel button for quit
# GUI
heart_image = pg.image.load('assets/images/gui/heart.png').convert_alpha()
coin_image = pg.image.load('assets/images/gui/coin.png').convert_alpha()
token_image = pg.image.load('assets/images/gui/token.png').convert_alpha()
logo_image = pg.image.load('assets/images/gui/logo.png').convert_alpha()

# Download json data for level
with open('levels/level_1_data.json') as file:
    world_data = json.load(file)

# Load fonts for displaying text
text_font = pg.font.SysFont("Consolas", 24, bold=True)
display_font = pg.font.SysFont("Consolas", 24, bold=True)
large_display_font = pg.font.SysFont("Consolas", 32, bold=True)
large_font = pg.font.SysFont("Consolas", 40)
title_font = pg.font.SysFont("Consolas", 72, bold=True)
little_font = pg.font.SysFont("Consolas", 12)


# Function for displaying text
def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))


def display_data():
    # Draw panel
    pg.draw.rect(screen, "Royal Blue 1", (SCREEN_WIDTH, 0, SIDE_PANEL, SCREEN_HEIGHT))
    pg.draw.rect(screen, "dim grey", (SCREEN_WIDTH, 0, SIDE_PANEL, 660), 7)  # Ramka
    pg.draw.rect(screen, "blue", (SCREEN_WIDTH, 660, SIDE_PANEL, 960))
    pg.draw.rect(screen, "dim grey", (SCREEN_WIDTH, 653, SIDE_PANEL, 307), 7)  # Ramka

    draw_text("Jak grać:", large_display_font, "grey100", SCREEN_WIDTH + 10, 665)
    draw_text("-kup i postaw wieże", display_font, "grey100", SCREEN_WIDTH + 10, 695 + 8 + 3 + 3)
    draw_text("   [BUY TURRET]", display_font, "grey100", SCREEN_WIDTH + 10, 695 + 30 + 8 + 3 + 3)
    draw_text("-zacznij grę", display_font, "grey100", SCREEN_WIDTH + 10, 695 + 60 + 8 + 3 + 3 + 3)
    draw_text("   [START THE GAME]", display_font, "grey100", SCREEN_WIDTH + 10, 695 + 90 + 8 + 3 + 3)
    draw_text("-ulepsz wieże", display_font, "grey100", SCREEN_WIDTH + 10, 695 + 120 + 8 + 3 + 3 + 3)
    draw_text("   [UPGRADE]", display_font, "grey100", SCREEN_WIDTH + 10, 695 + 150 + 8 + 3 + 3 + 3)
    draw_text("-przetrwaj 15 leveli", display_font, "grey100", SCREEN_WIDTH + 10, 695 + 180 + 8 + 3 + 3 + 3 + 3)
    draw_text("assets used:", little_font, "grey100", SCREEN_WIDTH - 270, SCREEN_HEIGHT - 60)
    draw_text("Pixel UI pack by Kenney Vleugels [CC0]", little_font, "grey100", SCREEN_WIDTH - 270, SCREEN_HEIGHT - 45)
    draw_text("Board Game by Kenney Vleugels [CC0]", little_font, "grey100", SCREEN_WIDTH - 270, SCREEN_HEIGHT - 30)
    draw_text("Ground Shaker by Zintoki [CC0]", little_font, "grey100", SCREEN_WIDTH - 270, SCREEN_HEIGHT - 15)

    # Display data
    draw_text("LEVEL:" + str(world.level), text_font, "grey100", SCREEN_WIDTH + 10, 15)
    screen.blit(heart_image, (SCREEN_WIDTH + 10, 35))
    draw_text(str(world.health), text_font, "grey100", SCREEN_WIDTH + 75, 55)
    screen.blit(coin_image, (SCREEN_WIDTH + 10, 95))
    draw_text(str(world.money), text_font, "grey100", SCREEN_WIDTH + 75, 116)


def create_turret(pos):
    mouse_tile_x = pos[0] // TILE_SIZE
    mouse_tile_y = pos[1] // TILE_SIZE
    # Calculate sequential number of a mouse tile
    mouse_tile_num = (mouse_tile_y * COLS) + mouse_tile_x
    # Check if tile is grass (test - 120)
    if world.tile_map[mouse_tile_num] in FREE_SPACE and world.objects[mouse_tile_num] == 0:
        # Check if there is not a turret
        space_is_free = True
        for turret in turret_group:
            if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
                space_is_free = False
        # If it is free - create turret
        if space_is_free:
            new_turret = Turret(turret_spritesheets, mouse_tile_x, mouse_tile_y, world)
            turret_group.add(new_turret)
            # Deduct cost of the turret from player
            world.money -= BUY_COST


def select_turret(pos):
    mouse_tile_x = pos[0] // TILE_SIZE
    mouse_tile_y = pos[1] // TILE_SIZE
    for turret in turret_group:
        if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
            return turret


def clear_selection():
    for turret in turret_group:
        turret.selected = False


def draw_menu():
    # Screen is already filled with maroon color before this function is called

    # Calculate the center of the screen (including side panel)
    center_x = (SCREEN_WIDTH + SIDE_PANEL) // 2
    center_y = SCREEN_HEIGHT // 2

    # Draw a border for the menu - centered on screen
    menu_width = 600
    menu_height = 500
    menu_rect = pg.Rect(center_x - menu_width // 2, center_y - menu_height // 2, menu_width, menu_height)
    pg.draw.rect(screen, "blue", menu_rect, border_radius=15)
    pg.draw.rect(screen, "dim grey", menu_rect, 7, border_radius=15)

    # Draw the game logo at the top of the menu
    logo_rect = logo_image.get_rect(center=(center_x, menu_rect.top + 100))
    screen.blit(logo_image, logo_rect)

    # Draw the game title - centered
    title_text = title_font.render("TOWER DEFENCE", True, "grey100")
    title_rect = title_text.get_rect(center=(center_x, menu_rect.top + 200))
    screen.blit(title_text, title_rect)

    author_text = large_display_font.render("by Mateusz Majewski", True, "grey100")
    author_rect = author_text.get_rect(center=(center_x, menu_rect.top + 280))
    screen.blit(author_text, author_rect)

    # Draw buttons - centered
    play_button = Button(center_x - 120, menu_rect.top + 350, play_button_image, True)
    quit_button = Button(center_x - 120, menu_rect.top + 420, quit_button_image, True)

    # Return button states
    play_clicked = play_button.draw(screen)
    quit_clicked = quit_button.draw(screen)

    # Draw button labels
    draw_text("GRAJ", large_display_font, "grey100", center_x, menu_rect.top + 357)
    draw_text("WYJDŹ", large_display_font, "grey100", center_x, menu_rect.top + 427)

    return play_clicked, quit_clicked


# Creating world
world = World(world_data, map_image)
world.process_data()
world.process_enemies()

# Create groups
enemy_group = pg.sprite.Group()
turret_group = pg.sprite.Group()

# Create buttons
turret_button = Button(SCREEN_WIDTH + 15, 170, buy_turret_image, True)
upgrade_button = Button(SCREEN_WIDTH + 15, 250, upgrade_turret_image, True)
cancel_button = Button(SCREEN_WIDTH + 54, 330, cancel_image, True)
begin_button = Button(SCREEN_WIDTH + 54, 458, begin_image, True)
fast_forward_button = Button(SCREEN_WIDTH + 54, 458, fast_forward_image, False)  # TODO change on click to true
restart_button = Button(384, 440, restart_image, True)
continue_button = Button(384, 515, continue_image, True)

# Game loop
run = True
while run:
    clock.tick(FPS)

    # Event handler
    for event in pg.event.get():
        # Quit
        if event.type == pg.QUIT:
            run = False
        # Mouse click
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pg.mouse.get_pos()

            if game_state == GameState.PLAYING:
                # Check if mouse is on game area
                if mouse_pos[0] < SCREEN_WIDTH and mouse_pos[1] < SCREEN_HEIGHT:
                    # Clear selected turrets
                    selected_turret = None
                    clear_selection()
                    if placing_turrets:
                        # Check if there is enough money
                        if world.money >= BUY_COST:
                            create_turret(mouse_pos)
                    else:
                        selected_turret = select_turret(mouse_pos)

    # Update based on game state
    if game_state == GameState.PLAYING:
        ##########
        # UPDATE #
        ##########

        # Check if player has lost
        if world.health <= 0:
            game_state = GameState.GAME_OVER
            game_outcome = -1  # Loss

        # Update groups
        enemy_group.update()
        turret_group.update(enemy_group)

        # Highlight selected turret
        if selected_turret:
            selected_turret.selected = True

        ########
        # DRAW #
        ########

        # Draw level
        world.draw(screen)

        # Draw groups
        enemy_group.draw(screen)
        for turret in turret_group:
            turret.draw(screen)

        display_data()

        # Check if the level started
        if level_started == False:
            if begin_button.draw(screen):
                level_started = True
        else:
            # Fast forward
            world.game_speed = 1
            if fast_forward_button.draw(screen):
                world.game_speed = 2

            # Spawn enemies
            if pg.time.get_ticks() - last_enemy_spawn > SPAWN_COOLDOWN:
                if world.spawn_enemies < len(world.enemy_list):
                    enemy_type = world.enemy_list[world.spawn_enemies]
                    enemy = Enemy(enemy_type, world.waypoints, enemy_images, world)
                    enemy_group.add(enemy)
                    world.spawn_enemies += 1
                    last_enemy_spawn = pg.time.get_ticks()

        # Check if level is finished
        if level_started and world.check_level_completion():
            world.money += LEVEL_COMPLETE_REWARD
            world.level_complete = True
            level_started = False

            # Check if this was the final level
            if world.level >= world.max_level:
                world.game_complete = True
            else:
                # Prepare for the next level
                world.level += 1
                world.reset_level()
                world.process_enemies()

        if world.game_complete:
            game_outcome = 1
            game_state = GameState.GAME_OVER

        # Draw buttons for gameplay
        # Show cost of turret
        draw_text(str(BUY_COST), text_font, "grey100", SCREEN_WIDTH + 215, 190)
        screen.blit(token_image, (SCREEN_WIDTH + 255, 184))
        if turret_button.draw(screen):
            placing_turrets = True

        # If placing turrets, show cancel button
        if placing_turrets:
            # Show cursor turret
            cursor_rect = cursor_turret.get_rect()
            cursor_pos = pg.mouse.get_pos()
            cursor_rect.center = cursor_pos
            if cursor_pos[0] <= SCREEN_WIDTH:
                screen.blit(cursor_turret, cursor_pos)
            if cancel_button.draw(screen):
                placing_turrets = False

        # If a turret is selected, display upgrade button
        if selected_turret:
            # If turret can be upgraded
            if selected_turret.upgrade_level < TURRET_LEVELS:
                draw_text(str(UPGRADE_COST), text_font, "grey100", SCREEN_WIDTH + 215, 269)
                screen.blit(token_image, (SCREEN_WIDTH + 255, 263))
                if upgrade_button.draw(screen):
                    if world.money >= UPGRADE_COST:
                        selected_turret.upgrade()
                        world.money -= UPGRADE_COST

    elif game_state == GameState.GAME_OVER:
        # Draw the game over screen
        # Keep showing the game in the background
        world.draw(screen)
        enemy_group.draw(screen)
        for turret in turret_group:
            turret.draw(screen)
        display_data()

        # Draw game over dialog
        pg.draw.rect(screen, "Royal Blue 1", (290, 350, 380, 260), border_radius=7)
        pg.draw.rect(screen, "dim grey", (290, 350, 380, 260), 7, border_radius=7)

        if game_outcome == -1:
            draw_text("GAME OVER", large_font, "grey0", 378, 375)
            if restart_button.draw(screen):
                game_state = GameState.PLAYING
                level_started = False
                placing_turrets = False
                selected_turret = None
                last_enemy_spawn = pg.time.get_ticks()
                world = World(world_data, map_image)
                world.process_data()
                world.process_enemies()
                enemy_group.empty()
                turret_group.empty()
            if continue_button.draw(screen):
                run = False  # Exit the game when continue is clicked

        elif game_outcome == 1:
            draw_text("YOU WIN", large_font, "grey0", 410, 375)
            # Restart level
            if restart_button.draw(screen):
                game_state = GameState.PLAYING
                level_started = False
                placing_turrets = False
                selected_turret = None
                last_enemy_spawn = pg.time.get_ticks()
                world = World(world_data, map_image)
                world.process_data()
                world.process_enemies()
                enemy_group.empty()
                turret_group.empty()
            if continue_button.draw(screen):
                run = False  # Exit the game when continue is clicked

    pg.display.flip()

pg.quit()