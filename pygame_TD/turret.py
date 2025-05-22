import pygame as pg
import math
from constants import *
from turret_data import TURRET_DATA
from world import World


class Turret(pg.sprite.Sprite):
    def __init__(self, sprite_sheets, tile_x, tile_y, world):
        super().__init__()
        self.upgrade_level = 1
        self.range = TURRET_DATA[self.upgrade_level - 1].get("range")
        self.cooldown = (TURRET_DATA[self.upgrade_level - 1].get("cooldown") / world.game_speed)
        self.last_shot = pg.time.get_ticks()
        self.selected = False
        self.target = None

        # position variables
        self.tile_x = tile_x
        self.tile_y = tile_y
        # calculate center coordinates
        self.x = (self.tile_x + 0.5) * TILE_SIZE
        self.y = (self.tile_y + 0.5) * TILE_SIZE

        # animation variables
        self.sprite_sheets = sprite_sheets
        self.animation_list = self.load_images(self.sprite_sheets[self.upgrade_level - 1])
        self.frame_index = 0
        self.update_time = pg.time.get_ticks()
        self.animating = False  # czy aktualnie trwa animacja

        # update image
        self.angle = 90
        self.original_image = self.animation_list[self.frame_index]
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

        #create circle showing range
        self.range_image = pg.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pg.draw.circle(self.range_image, "gray100", (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center

    def load_images(self, sprite_sheet):
        # extract images from sheets
        size = sprite_sheet.get_height()
        animation_list = []
        for x in range(ANIMATION_STEPS):
            temp_img = sprite_sheet.subsurface(x * size, 0, size, size)
            animation_list.append(temp_img)
        return animation_list

    def update(self, enemy_group):
        #if target picked play firing animation
        if self.target:
            self.play_animation()
        else:
            #if pg.time.get_ticks() - self.last_shot > (self.cooldown / world.game_speed):
            self.pick_target(enemy_group)

    def pick_target(self, enemy_group):
        #find an enemy to target
        x_dist = 0
        y_dist = 0
        #check distance
        for enemy in enemy_group:
            if enemy.health > 0:
                x_dist = enemy.pos[0] - self.x
                y_dist = enemy.pos[1] - self.y
                dist = math.sqrt(x_dist ** 2 + y_dist ** 2)
                if dist < self.range:
                    self.target = enemy
                    self.angle = math.degrees(math.atan2(-y_dist, x_dist))
                    #damage enemy
                    self.target.health -= DAMAGE
                    #TODO damage
                    break

    def play_animation(self):
        current_time = pg.time.get_ticks()

        # Sprawdzamy czy można strzelić (cooldown)
        if current_time - self.last_shot > self.cooldown:
            self.last_shot = current_time
            self.animating = True  # rozpoczynamy animację
            self.frame_index = 0  # resetujemy animację

        # Aktualizacja animacji jeśli trwa
        if self.animating:
            if current_time - self.update_time > ANIMATION_DELAY:
                self.update_time = current_time
                self.frame_index += 1

                # Sprawdzamy czy animacja się zakończyła
                if self.frame_index >= len(self.animation_list):
                    self.frame_index = 0
                    self.animating = False
                    self.target = None

            # Aktualizacja obrazu niezależnie od tego czy zmieniła się klatka
            self.original_image = self.animation_list[self.frame_index]

    def upgrade(self):
        self.upgrade_level += 1
        self.range = TURRET_DATA[self.upgrade_level - 1].get("range")
        self.cooldown = TURRET_DATA[self.upgrade_level - 1].get("cooldown")

        #upgrade turret image
        self.animation_list = self.load_images(self.sprite_sheets[self.upgrade_level - 1])
        self.original_image = self.animation_list[self.frame_index]

        #upgrade range circle
        self.range_image = pg.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pg.draw.circle(self.range_image, "gray100", (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center

    def draw(self, surface):
        self.image = pg.transform.rotate(self.original_image, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

        surface.blit(self.image, self.rect)
        if self.selected:
                surface.blit(self.range_image, self.range_rect)