#!/usr/bin/env python
# encoding: utf-8


# this program is a small clone of Slayin,
# a game in which you're a soldier fighting monsters in a 2d world.
# a monster is killed upon colliding with soldier's sword.
# only controls used are left/right arrows to move and up arrow to jump.
# feel free to checkout Slayin trailer: http://youtu.be/GC003ZiXkt8
# or go ahead and buy it: https://itunes.apple.com/us/app/slayin/id548580856


# imports
import random
from time import time

import pygame

from pygame import display
from pygame.locals import QUIT


# globals
WIDTH = 640
HEIGHT = 320
FPS = 60.0


# classes
class Player():
    '''
    Player class - an object capable of moving left/right, jumping, holds a weapon.

    '''

    def __init__(self, canvas, x, y, w, h, color, direction, jump_direction, jump_height, gravity, health):
        '''Constructor, takes player's properties, like:

        (canvas, int, int, int, int, int, int, tuple, int)

        '''

        self.canvas = canvas
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.direction = direction
        self.jump_direction = jump_direction
        self.jump_height = jump_height
        self.gravity = gravity
        self.health = health

        self.invulnerable = 0

    def draw(self, weapon):
        '''This function simply draws a rectangle that represents player's position,
        as well as his weapon.
        '''

        rect = (self.x, self.y, self.w, self.h)
        pygame.draw.rect(self.canvas, self.color, rect)

        if self.direction > 0:
            weapon.x = self.x + self.w
            weapon.y = self.y + 10
            weapon.draw()

        else:
            weapon.x = self.x - weapon.w
            weapon.y = self.y + 10
            weapon.draw()

    def move(self):
        '''This function allows the player to move based on desired direction
        '''

        # moving horizontally
        if self.direction < 0 and self.x > 0:
            self.x += 3 * self.direction

        if self.direction > 0 and self.x + self.w < WIDTH:
            self.x += 3 * self.direction

        # moving vertically
        self.y += 15 * self.jump_direction * self.gravity

        if self.jump_direction < 0:
            self.gravity *= 0.82

        else:
            self.gravity *= 1.18

        if self.gravity <= 0.3:
            self.jump_direction *= -1

        if self.y >= 200:
            self.jump_direction = 0
            self.y = 200
            self.gravity = 2

    def jump(self):
        '''This function allows the player to jump
        '''

        # if player is on the ground - he can jump
        if self.y + self.h == 240:
            self.jump_direction = -1

    def invulnerability(self):
        '''After being hit by an enemy the player is invulnerable for a period of time
        '''

        if self.invulnerable > 0.01:
            self.invulnerable -= 0.01

        else:
            self.invulnerable = 0


class Weapon():
    '''Weapon class - allows killing enemies, is always in front of the player.
    '''

    def __init__(self, canvas, x, y, w, h, color):
        '''
        '''

        self.canvas = canvas
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color

    def draw(self):
        '''This function draws the weapon in front of the player.
        '''

        rect = (self.x, self.y, self.w, self.h)
        pygame.draw.rect(self.canvas, self.color, rect)


class Enemy():
    '''Enemy class - allows spawning of the enemies and their movement.
    '''

    def __init__(self, canvas, x, y, w, h, color, health):
        '''Constructor, takes enemy's properties:

        (canvas, int, int, int, int, tuple, int)

        '''

        self.canvas = canvas
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.health = health
        self.current_time = time()
        self.move_interval = 1.5
        self.direction = 0

    def draw(self):
        '''This function simply draws a rectangle that represents an enemy.
        '''

        rect = (self.x, self.y, self.w, self.h)
        pygame.draw.rect(self.canvas, self.color, rect)

    def move(self):
        '''This function takes care of enemy's movement(including spawning).
        '''

        # spawning
        if self.y > 200:
            self.y -= 1

        # changing moving direction
        if time() - self.current_time >= self.move_interval:
            self.direction = random.randint(-1, 1)
            self.current_time = time()

        # moving horizontally
        if self.direction < 0 and self.x > 0:
            self.x += 0.5 * self.direction

        if self.direction > 0 and self.x + self.w < WIDTH:
            self.x += 0.5 * self.direction


class FlyingEnemy(Enemy):
    '''This is a class for flying enemies - very similiar to Enemy, except they move differently.
    '''

    def move(self):
        '''This function takes care of flying enemy's movement(including spawning and descending).
        '''

        # spawning
        if self.y < 80:
            self.y += 1
            self.descend_level = 0
            self.descending_interval = 0
            self.move_interval = 4

        # changing moving direction
        if time() - self.current_time >= self.move_interval:
            self.direction = random.randint(-1, 1)
            self.current_time = time()

            # descending
            self.descending_interval += 1
            if self.descending_interval == 2:
                self.descending_interval = 0

                self.descend_level = 40

        # moving vertically
        if self.descend_level > 0:
            if self.y < 200:
                self.y += 1
                self.descend_level -= 1

        # moving horizontally
        if self.direction < 0 and self.x > 0:
            self.x += 0.7 * self.direction

        if self.direction > 0 and self.x + self.w < WIDTH:
            self.x += 0.7 * self.direction


class Medkit():
    '''This is a powerup that gives the player additional health.
    '''

    def __init__(self, canvas, x, y, w, h, color, health):
        '''Constructor method, takes all the important information to create a medkit.
        '''

        self.canvas = canvas
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.health = health

    def draw(self):
        '''This function draws a medkit.
        '''

        rect = (self.x, self.y, self.w, self.h)
        pygame.draw.rect(self.canvas, self.color, rect)

    def move(self):
        '''Medkit falls from the sky and stops when hits the ground.
        '''

        if self.y < HEIGHT - 80 - self.h:
            self.y += 2


# functions
def collision(object1, object2, obj1_type, obj2_type):
    '''This function takes 2 objects of a class and checks if they collided.
    '''

    if object1.x + object1.w > object2.x and object2.x + object2.w > object1.x and \
       object1.y + object1.h > object2.y and object2.y + object2.h > object1.y:

        # collision for enemies(they collide with player and weapons)
        if obj1_type == "enemy" or obj2_type == "enemy":
            # if obj1 is an enemy, obj2 is either player or weapon
            if obj1_type == "enemy":
                if obj2_type == "player":
                    if object2.invulnerable == 0:
                        object2.health -= 1
                        print("You've been hit! %d lives left!" % object2.health)
                        object2.invulnerable = 0.5

                else:
                    object1.health -= 1

            # if obj2 is an enemy, obj1 is either player or weapon
            else:
                if obj1_type == "player":
                    if object1.invulnerable == 0:
                        object1.health -= 1
                        print("You've been hit! %d lives left!" % object1.health)
                        object1.invulnerable = 0.5

                else:
                    object2.health -= 1

        # collision for medkits(they collide only with player)
        elif obj1_type == "medkit" or obj2_type == "medkit":
            if obj1_type == "medkit":
                if obj2_type == "player":
                    object2.health += 1
                    object1.health -= 1
                    print("You've obtained a medkit! %d lives left!" % object2.health)

            else:
                if obj1_type == "player":
                    object1.health += 1
                    object2.health -= 1
                    print("You've obtained a medkit! %d lives left!" % object1.health)


def display_score(time_at_start, score):
    time_played = "%.2f" % (time() - time_at_start)
    score_message = "\nYou've been playing for {0} seconds and you've slain {1} enemies!!\nThanks for playing!!\n"
    print(score_message.format(time_played, score))


def main():
    # setup pygame
    pygame.init()
    canvas = display.set_mode((WIDTH, HEIGHT), 0, 16)
    display.set_caption('Slayin Clone')

    # variables
    score = 0
    enemies = []
    medkits = []
    respawn_time = 0.5
    flying_enemy_spawn_interval = 0
    medkit_spawn_interval = 0

    # create the player
    player = Player(canvas, 300, 200, 40, 40, (210, 125, 44), 0, 0, 100, 1, 10)
    weapon = Weapon(canvas, 340, 210, 40, 15, (117, 113, 97))

    time_at_start = time()
    current_time = time()
    prev_frame_time = time()

    # main loop
    while True:
        current_frame_time = time()

        if (current_frame_time - prev_frame_time) >= (1.0 / FPS):
            prev_frame_time = time()

            # fill the screen with background color
            canvas.fill((222, 238, 214))

            # spawning enemies
            if time() - current_time >= respawn_time:
                enemies.append(Enemy(canvas, random.randint(0, WIDTH - 40), HEIGHT, 40, 40, (89, 125, 206), 1))
                current_time = time()

                flying_enemy_spawn_interval += 1
                if flying_enemy_spawn_interval == 10:
                    flying_enemy_spawn_interval = 0
                    enemies.append(FlyingEnemy(canvas, random.randint(0, WIDTH - 40), -40, 40, 40, (89, 125, 206), 1))

                medkit_spawn_interval += 1
                if medkit_spawn_interval == 30:
                    medkit_spawn_interval = 0
                    medkits.append(Medkit(canvas, random.randint(0, WIDTH - 20), -20, 20, 20, (109, 170, 44), 1))

                if score != 0 and score % 10 == 0:
                    if respawn_time > 0.2:
                        respawn_time -= 0.01

            # draw ground
            rect = (0, 240, 640, 80)
            pygame.draw.rect(canvas, (20, 18, 28), rect)

            # player handling
            # move player
            player.move()

            # draw player
            player.draw(weapon)

            # invulnerability handling
            player.invulnerability()

            # enemies handling
            for enemy in enemies:
                # move enemy
                enemy.move()

                # draw enemy
                enemy.draw()

            # medkits handling
            for i, medkit in enumerate(medkits):
                medkit.move()

                medkit.draw()

                # collision detecion
                collision(medkit, player, "medkit", "player")

                if medkit.health == 0:
                    del medkits[i]

            # collision handling
            # player collides with enemies
            for i, enemy in enumerate(enemies):
                collision(enemy, weapon, "enemy", "weapon")
                collision(enemy, player, "enemy", "player")

                if enemy.health == 0:
                    score += 1
                    print("You've slain an enemy! Your score is %d!" % score)
                    del enemies[i]

            # update display
            display.update()

            # if player has no health - stop the game
            if player.health == 0:
                break

            # handling events
            for event in pygame.event.get():
                # handling movement
                # left(user presses left arrow)
                if event.type == 2:
                    if pygame.key.name(event.key) == "left":
                        player.direction = -1

                    # right(user presses right arrow)
                    if pygame.key.name(event.key) == "right":
                        player.direction = 1

                    # jump(user presses space)
                    if pygame.key.name(event.key) == "up":
                        player.jump()

                    # closing the program
                    if pygame.key.name(event.key) == "escape":
                        display_score(time_at_start, score)
                        pygame.quit()
                        exit()

                # handling quit event
                if event.type is QUIT:
                    display_score(time_at_start, score)
                    pygame.quit()
                    exit()

    display_score(time_at_start, score)

    while True:
        for event in pygame.event.get():
            # handling quit event
            if event.type is QUIT:
                pygame.quit()
                exit()

            # closing the program
            if event.type == 2:
                if pygame.key.name(event.key) == "escape":
                    pygame.quit()
                    exit()

                if pygame.key.name(event.key) == "r":
                    main()


if __name__ == '__main__':
    main()
