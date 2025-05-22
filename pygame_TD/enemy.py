import pygame as pg
from pygame.math import Vector2
import math
from enemy_data import ENEMY_DATA
from world import *
from constants import *

class Enemy(pg.sprite.Sprite):
    def __init__(self, enemy_type, waypoints, images, world):
        pg.sprite.Sprite.__init__(self)
        self.world = world
        self.waypoints = waypoints
        self.pos = Vector2(waypoints[0])
        self.target_waypoint = 1
        self.health = ENEMY_DATA.get(enemy_type)["health"]
        self.speed = ENEMY_DATA.get(enemy_type)["speed"]
        self.angle = 0
        self.original_image = images.get(enemy_type)
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def update(self):
        self.move()
        self.rotate()
        self.check_alive()

    def move(self):
        if self.target_waypoint < len(self.waypoints):
            self.target = Vector2(self.waypoints[self.target_waypoint])
            self.movement = self.target - self.pos
        else:
            self.kill()
            self.world.health -= 10
            self.world.missed_enemies += 1

        dist = self.movement.length()

        if dist >= (self.speed * self.world.game_speed):
            self.pos += self.movement.normalize() * (self.speed * self.world.game_speed)
        else:
            if dist != 0:
                self.pos += self.movement.normalize() * dist
            self.target_waypoint += 1

    def rotate(self):
        dist = self.target - self.pos
        self.angle = -90
        self.angle = math.degrees(math.atan2(-dist[1], dist[0])) + 90

        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def check_alive(self):
        if self.health <= 0:
            self.world.killed_enemies += 1
            self.world.money += KILL_REWARD
            self.kill()