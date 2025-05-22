import pygame as pg
import random
from constants import *
from enemy_data import ENEMY_SPAWN_DATA


class World():
    def __init__(self, data, map_image):
        self.level = 1
        self.game_speed = 1
        self.health = HEALTH
        self.money = MONEY
        self.objects = []
        self.tile_map = []
        self.waypoints = []
        self.level_data = data
        self.image = map_image
        self.enemy_list = []
        self.spawn_enemies = 0
        self.killed_enemies = 0
        self.missed_enemies = 0
        self.max_level = len(ENEMY_SPAWN_DATA)
        self.game_complete = False
        self.level_complete = False

    def process_data(self):
        # look through data to extract wanted info
        for layer in self.level_data["layers"]:
            if layer["name"] == "path":
                self.tile_map = layer["data"]
            elif layer["name"] == "waypoints":
                for obj in layer["objects"]:
                    waypoint_data = obj["polyline"]
                    self.process_waypoints(waypoint_data)
            elif layer["name"] == "objects":
                self.objects = layer["data"]

    def process_waypoints(self, data):
        # iterate through waypoints to extract individual x and y coordinates
        for point in data:
            temp_x = point.get("x")
            temp_y = point.get("y")
            self.waypoints.append((temp_x, temp_y))

    def process_enemies(self):
        # Check if the level exists in enemy spawn data
        if self.level > self.max_level:
            # Set game complete flag or handle max level differently
            self.game_complete = True
            self.enemy_list = []  # No more enemies to spawn
            return

        # Process enemies for the current level
        enemies = ENEMY_SPAWN_DATA[self.level - 1]
        self.enemy_list = []
        for enemy_type in enemies:
            enemies_to_spawn = enemies[enemy_type]
            for _ in range(enemies_to_spawn):
                self.enemy_list.append(enemy_type)
        random.shuffle(self.enemy_list)

    def check_level_completion(self):
        # Only consider level complete when:
        # 1. We have a valid enemy list with at least one enemy
        # 2. All enemies have been spawned
        # 3. All spawned enemies have been either killed or missed

        if len(self.enemy_list) == 0:
            return False

        # Check if all enemies have been spawned
        all_spawned = self.spawn_enemies >= len(self.enemy_list)

        # Check if all spawned enemies have been accounted for
        all_processed = (self.killed_enemies + self.missed_enemies) >= len(self.enemy_list)

        # Debug information - can be removed later
        # print(f"Level: {self.level}, Spawned: {self.spawn_enemies}/{len(self.enemy_list)}, " +
        #       f"Killed: {self.killed_enemies}, Missed: {self.missed_enemies}, " +
        #       f"Total processed: {self.killed_enemies + self.missed_enemies}")

        return all_spawned and all_processed

    def reset_level(self):
        self.level_complete = False
        self.spawn_enemies = 0
        self.killed_enemies = 0
        self.missed_enemies = 0
        self.enemy_list = []

    def reset_game(self):
        self.level = 1
        self.health = HEALTH
        self.money = MONEY
        self.game_complete = False
        self.level_complete = False
        self.reset_level()

    def draw(self, surface):
        surface.blit(self.image, (0, 0))