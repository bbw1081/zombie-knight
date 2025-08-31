import pygame, random
from tile import Tile
from player import Player
from bullet import Bullet
from zombie import Zombie
from ruby_maker import RubyMaker
from ruby import Ruby
from portal import Portal

"""GAME SETUP"""
#Initialize Pygame
pygame.init()

#use 2d vectors
VECTOR = pygame.math.Vector2

#Set Display Surface
##tile height is 32x32; 40 tiles wide & 23 tiles high
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 736
DISPLAY_SURFACE = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Zombie Knight!")

#Set FPS and Clock
FPS = 60
CLOCK = pygame.time.Clock()

class Game:
    """A class to help manage gameplay"""

    def __init__(self):
        """Initialize the game"""
        #set constant variables
        self.STARTING_ROUND_TIME = 30

        #set game values
        self.score = 0
        self.round_number = 1
        self.frame_count = 0
        self.round_time = self.STARTING_ROUND_TIME

        #load in fonts
        self.title_font = pygame.font.Font("assets/fonts/Poultrygeist.ttf", 48)
        self.HUD_font = pygame.font.Font("assets/fonts/Pixel.ttf", 24)

    def update(self):
        """update the game"""
        #update the round time every second
        self.frame_count += 1
        if self.frame_count % FPS == 0:
            self.round_time -= 1
            self.frame_count = 0

    def draw(self):
        """draw the game HUD"""
        #define colors
        WHITE = (255, 255, 255)
        GREEN = (25, 200, 25)

        #set text
        score_text = self.HUD_font.render("Score: " + str(self.score), True, WHITE)
        score_rect = score_text.get_rect()
        score_rect.topleft = (10, WINDOW_HEIGHT - 50)

        health_text = self.HUD_font.render("Health: " + str(100), True, WHITE)
        health_rect = health_text.get_rect()
        health_rect.topleft = (10, WINDOW_HEIGHT - 25)

        title_text = self.title_font.render("Zombie Knight", True, GREEN)
        title_rect = title_text.get_rect()
        title_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 25)

        round_text = self.HUD_font.render("Night: " + str(self.round_number), True, WHITE)
        round_rect = round_text.get_rect()
        round_rect.topright = (WINDOW_WIDTH - 10, WINDOW_HEIGHT - 50)

        time_text = self.HUD_font.render("Sunrise in: " + str(self.round_time), True, WHITE)
        time_rect = time_text.get_rect()
        time_rect.topright = (WINDOW_WIDTH - 10, WINDOW_HEIGHT - 25)

        #draw the HUD
        DISPLAY_SURFACE.blit(score_text, score_rect)
        DISPLAY_SURFACE.blit(health_text, health_rect)
        DISPLAY_SURFACE.blit(title_text, title_rect)
        DISPLAY_SURFACE.blit(round_text, round_rect)
        DISPLAY_SURFACE.blit(time_text, time_rect)


    def add_zombie(self):
        """add a zombie to the game"""
        pass

    def check_collisions(self):
        """Check collisions that affect gameplay"""
        pass

    def check_round_completion(self):
        """Check if the player survived a night"""
        pass

    def check_game_over(self):
        """Check to see if the player lost the game"""
        pass

    def start_new_round(self):
        """start a new night"""
        pass

    def pause_game(self):
        """pause the game"""
        pass

    def reset_game(self):
        """reset the game"""
        pass


#Create Sprite Groups
main_tile_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()

player_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()

zombie_group = pygame.sprite.Group()

portal_group = pygame.sprite.Group()
ruby_group = pygame.sprite.Group()

#Create the tile map
#0 --> no tile, 1 --> dirt tile, 2-5 --> platforms, 6 --> ruby maker, 7-8 --> portals, 9 --> player
#23 rows and 40 columns
tile_map = [
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0],
[4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[4, 4, 4, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 4, 4, 4],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0],
[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

#generate tile objects from tile map
#loop through the 23 rows in the map, i moves us down the map
for i in range(len(tile_map)):
    #loop through the 40 columns in a given row, j moves us across the map
    for j in range(len(tile_map[i])):
        #dirt tile
        if tile_map[i][j] == 1:
            Tile(j*32, i*32, 1, main_tile_group)
        #ground platform tile
        elif tile_map[i][j] == 2:
            Tile(j*32, i*32, 2, main_tile_group, platform_group)
        #left platform tile
        elif tile_map[i][j] == 3:
            Tile(j*32, i*32, 3, main_tile_group, platform_group)
        #middle platform tile
        elif tile_map[i][j] == 4:
            Tile(j*32, i*32, 4, main_tile_group, platform_group)
        #right platform tile
        elif tile_map[i][j] == 5:
            Tile(j*32, i*32, 5, main_tile_group, platform_group)
        #ruby maker
        elif tile_map[i][j] == 6:
            RubyMaker(j*32, i*32, main_tile_group)
        #portals
        elif tile_map[i][j] == 7:
            Portal(j*32, i*32, "green", portal_group)
        elif tile_map[i][j] == 8:
            Portal(j*32, i*32, "purple", portal_group)
        #player
        elif tile_map[i][j] == 9:
            pass


#Load in background image
background_image = pygame.transform.scale(pygame.image.load("assets/images/background.png"),
                                          (WINDOW_WIDTH, WINDOW_HEIGHT))
background_rect = background_image.get_rect()
background_rect.topleft = (0,0)

#create a game
my_game = Game()

"""MAIN GAME LOOP"""
running = True
while running:
    #Check to see if user wants to quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #blit the background
    DISPLAY_SURFACE.blit(background_image, background_rect)

    #draw our tiles
    main_tile_group.update()
    main_tile_group.draw(DISPLAY_SURFACE)

    #draw and update sprite groups
    portal_group.update()
    portal_group.draw(DISPLAY_SURFACE)

    #update and draw game
    my_game.update()
    my_game.draw()

    #update display and tick clock
    pygame.display.update()
    CLOCK.tick(FPS)

#end the game
pygame.quit()
