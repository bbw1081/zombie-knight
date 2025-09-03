import pygame, random

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

#DEFINE CLASSES
class Game:
    """A class to help manage gameplay"""

    def __init__(self, player, zombie_group, platform_group, portal_group, bullet_group, ruby_group):
        """Initialize the game"""
        #set constant variables
        self.STARTING_ROUND_TIME = 30
        self.STARTING_ZOMBIE_CREATION_TIME = 5

        #set game values
        self.score = 0
        self.round_number = 1
        self.frame_count = 0
        self.round_time = self.STARTING_ROUND_TIME
        self.zombie_creation_time = self.STARTING_ZOMBIE_CREATION_TIME

        #load in fonts
        self.title_font = pygame.font.Font("assets/fonts/Poultrygeist.ttf", 48)
        self.HUD_font = pygame.font.Font("assets/fonts/Pixel.ttf", 24)

        #set sounds
        self.lost_ruby_sound = pygame.mixer.Sound("assets/sounds/lost_ruby.wav")
        self.ruby_pickup_sound = pygame.mixer.Sound("assets/sounds/ruby_pickup.wav")
        pygame.mixer.music.load("assets/sounds/level_music.wav")
        pygame.mixer.music.set_volume(0.4)

        #attach groups and sprites
        self.player = player
        self.zombie_group = zombie_group
        self.platform_group = platform_group
        self.portal_group = portal_group
        self.bullet_group = bullet_group
        self.ruby_group = ruby_group

    def update(self):
        """update the game"""
        #update the round time every second
        self.frame_count += 1
        if self.frame_count % FPS == 0:
            self.round_time -= 1
            self.frame_count = 0
        
        #do checks
        self.check_collisions()
        self.add_zombie()
        self.check_round_completion()
        self.check_game_over()

    def draw(self):
        """draw the game HUD"""
        #define colors
        WHITE = (255, 255, 255)
        GREEN = (25, 200, 25)

        #set text
        score_text = self.HUD_font.render("Score: " + str(self.score), True, WHITE)
        score_rect = score_text.get_rect()
        score_rect.topleft = (10, WINDOW_HEIGHT - 50)

        health_text = self.HUD_font.render("Health: " + str(self.player.health), True, WHITE)
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
        #check to add a zombie every second
        if self.frame_count % FPS == 0:
            #only add a zombie if zombie creation time has passed
            if self.round_time % self.zombie_creation_time == 0:
                self.zombie_group.add(Zombie(self.platform_group, self.portal_group, self.round_number, 5 + self.round_number))

    def check_collisions(self):
        """Check collisions that affect gameplay"""
        #see if any bullet hit any zombie
        collision_dict = pygame.sprite.groupcollide(self.bullet_group, self.zombie_group, True, False)
        if collision_dict:
            for zombies in collision_dict.values():
                for zombie in zombies:
                    zombie.hit_sound.play()
                    zombie.is_dead = True
                    zombie.animate_death = True

        #check for collisions between player and zombie
        collision_list = pygame.sprite.spritecollide(self.player, self.zombie_group, False)
        if collision_list:
            for zombie in collision_list:
                if zombie.is_dead:
                    #kill the zombie
                    zombie.kick_sound.play()
                    zombie.kill()
                    self.score += 25
                    self.ruby_group.add(Ruby(self.platform_group, self.portal_group))
                else:
                    #take damage
                    self.player.health -= 20
                    self.player.hit_sound.play()
                    #move the player to not continually take damage
                    self.player.position.x -= 256 * zombie.direction
                    self.player.rect.bottomleft = self.player.position

        #see if a player collided with a ruby
        if pygame.sprite.spritecollide(self.player, self.ruby_group, True):
            self.ruby_pickup_sound.play()
            self.score += 100
            self.player.health += 10
            if self.player.health > self.player.STARTING_HEALTH:
                self.player.health = self.player.STARTING_HEALTH
        
        #see if a living zombie collided with a ruby
        for zombie in self.zombie_group:
            if not zombie.is_dead:
                if pygame.sprite.spritecollide(zombie, self.ruby_group, True):
                    self.lost_ruby_sound.play()
                    self.zombie_group.add(Zombie(self.platform_group, self.portal_group, self.round_number, 5+self.round_number))

    def check_round_completion(self):
        """Check if the player survived a night"""
        if self.round_time <= 0:
            self.start_new_round()

    def check_game_over(self):
        """Check to see if the player lost the game"""
        if self.player.health <= 0:
            pygame.mixer.music.stop()
            self.pause_game("Game Over! Final Score " + str(self.score), "Press 'Enter' to play again")
            self.reset_game()

    def start_new_round(self):
        """start a new night"""
        self.round_number += 1

        #update zombie creation time
        if self.round_number < self.STARTING_ZOMBIE_CREATION_TIME:
            self.zombie_creation_time -= 1

        #reset round values
        self.round_time = self.STARTING_ROUND_TIME

        #empty groups
        self.zombie_group.empty()
        self.ruby_group.empty()
        self.bullet_group.empty()

        #reset the player
        self.player.reset()

        #pause the game
        self.pause_game("You survived the night!", "Press 'Enter' to continue...")

    def pause_game(self, main_text, sub_text, version_text=None):
        """pause the game"""
        global running

        pygame.mixer.music.pause()
        
        #set colors
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        GREEN = (25, 200, 25)

        #render text
        my_main_text = self.title_font.render(main_text, True, GREEN)
        main_rect = my_main_text.get_rect()
        main_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)

        my_sub_text = self.title_font.render(sub_text, True, WHITE)
        sub_rect = my_sub_text.get_rect()
        sub_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 64)

        #display the pause text
        DISPLAY_SURFACE.fill(BLACK)
        DISPLAY_SURFACE.blit(my_main_text, main_rect)
        DISPLAY_SURFACE.blit(my_sub_text, sub_rect)
        if version_text:
            my_version_text = self.HUD_font.render(version_text, True, WHITE)
            version_rect = my_version_text.get_rect()
            version_rect.bottomright = (WINDOW_WIDTH - 10, WINDOW_HEIGHT - 10)
            DISPLAY_SURFACE.blit(my_version_text, version_rect)

        pygame.display.update()

        #pause game until user hits enter or quits
        is_paused = True
        while is_paused:
            for event in pygame.event.get():
                #player wants to continue
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        is_paused = False
                        pygame.mixer.music.unpause()

                #player wants to quit
                if event.type == pygame.QUIT:
                    is_paused = False
                    running = False
                    pygame.mixer.music.stop()


    def reset_game(self):
        """reset the game"""
        
        #reset game values
        self.score = 0
        self.round_number = 1
        self.round_time = self.STARTING_ROUND_TIME
        self.zombie_creation_time = self.STARTING_ZOMBIE_CREATION_TIME

        #reset player
        self.player.health = self.player.STARTING_HEALTH
        self.player.reset()

        #empty sprite groups
        self.zombie_group.empty()
        self.ruby_group.empty()
        self.bullet_group.empty()

        #start music
        pygame.mixer.music.play(-1, 0.0)

class Player(pygame.sprite.Sprite):
    """A class the user controls"""

    def __init__(self, x, y, platform_group, portal_group, bullet_group):
        """initialize the player"""
        super().__init__()

        #set constant variables
        self.HORIZONTAL_ACCEL = 2
        self.HORIZONTAL_FRICTION = 0.15
        self.VERTICAL_ACCEL = 0.8 #gravity
        self.VERTICAL_JUMP_SPEED = 18 #determines how high the player can jump
        self.STARTING_HEALTH = 100

        #create animation lists
        self.move_right_sprites = []
        self.move_left_sprites = []
        self.idle_right_sprites = []
        self.idle_left_sprites = []
        self.jump_right_sprites = []
        self.jump_left_sprites = []
        self.attack_right_sprites = []
        self.attack_left_sprites = []

        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/run/Run (1).png"), (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/run/Run (2).png"), (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/run/Run (3).png"), (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/run/Run (4).png"), (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/run/Run (5).png"), (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/run/Run (6).png"), (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/run/Run (7).png"), (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/run/Run (8).png"), (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/run/Run (9).png"), (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/run/Run (10).png"), (64,64)))

        for sprite in self.move_right_sprites:
            self.move_left_sprites.append(pygame.transform.flip(sprite, True, False))

        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/idle/Idle (1).png"), (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/idle/Idle (2).png"), (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/idle/Idle (3).png"), (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/idle/Idle (4).png"), (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/idle/Idle (5).png"), (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/idle/Idle (6).png"), (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/idle/Idle (7).png"), (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/idle/Idle (8).png"), (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/idle/Idle (9).png"), (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/idle/Idle (10).png"), (64,64)))

        for sprite in self.idle_right_sprites:
            self.idle_left_sprites.append(pygame.transform.flip(sprite, True, False))

        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/jump/Jump (1).png"), (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/jump/Jump (2).png"), (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/jump/Jump (3).png"), (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/jump/Jump (4).png"), (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/jump/Jump (5).png"), (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/jump/Jump (6).png"), (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/jump/Jump (7).png"), (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/jump/Jump (8).png"), (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/jump/Jump (9).png"), (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/jump/Jump (10).png"), (64,64)))

        for sprite in self.jump_right_sprites:
            self.jump_left_sprites.append(pygame.transform.flip(sprite, True, False))

        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/attack/Attack (1).png"), (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/attack/Attack (2).png"), (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/attack/Attack (3).png"), (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/attack/Attack (4).png"), (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/attack/Attack (5).png"), (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/attack/Attack (6).png"), (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/attack/Attack (7).png"), (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/attack/Attack (8).png"), (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/attack/Attack (9).png"), (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/attack/Attack (10).png"), (64,64)))

        for sprite in self.attack_right_sprites:
            self.attack_left_sprites.append(pygame.transform.flip(sprite, True, False))

        #load image and get rect
        self.current_sprite = 0
        self.image = self.idle_right_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        #attach sprite groups
        self.platform_group = platform_group
        self.portal_group = portal_group
        self.bullet_group = bullet_group

        #animation booleans
        self.animate_jump = False
        self.animate_fire = False

        #load in sounds
        self.jump_sound = pygame.mixer.Sound("assets/sounds/jump_sound.wav")
        self.slash_sound = pygame.mixer.Sound("assets/sounds/slash_sound.wav")
        self.portal_sound = pygame.mixer.Sound("assets/sounds/portal_sound.wav")
        self.hit_sound = pygame.mixer.Sound("assets/sounds/player_hit.wav")

        #kinematics vectors
        self.position = VECTOR(x, y)
        self.velocity = VECTOR(0, 0)
        self.accel = VECTOR(0, self.VERTICAL_ACCEL) #gravity is affecting

        #set initial player values
        self.health = self.STARTING_HEALTH
        self.starting_x = x
        self.starting_y = y

    def update(self):
        """update the player"""
        self.move()
        self.check_collisions()
        self.check_animations()

        #update the player's mask
        self.mask = pygame.mask.from_surface(self.image)

    def move(self):
        """move the player"""
        #set the acceleration vector
        self.accel = VECTOR(0, self.VERTICAL_ACCEL)

        #check for key press and set horizontal acceleration
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.accel.x = -1 * self.HORIZONTAL_ACCEL
            self.animate(self.move_left_sprites, 0.5)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.accel.x = self.HORIZONTAL_ACCEL
            self.animate(self.move_right_sprites, 0.5)
        else:
            if self.velocity.x > 0:
                #animate right
                self.animate(self.idle_right_sprites, 0.5)
            else:
                self.animate(self.idle_left_sprites, 0.5)

        #calculate new kinematics values
        self.accel.x -= self.velocity.x * self.HORIZONTAL_FRICTION
        self.velocity += self.accel
        self.position += self.velocity + 0.5*self.accel

        #update rect and add wrap-around movement
        if self.position.x < 0:
            self.position.x = WINDOW_WIDTH
        elif self.position.x > WINDOW_WIDTH:
            self.position.x = 0

        self.rect.bottomleft = self.position

    def check_collisions(self):
        """checks for collisions with platforms and portals"""
        #collision check between player and platforms when falling
        if self.velocity.y > 0: #moving down
            collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False, pygame.sprite.collide_mask)
            if collided_platforms:
                self.position.y = collided_platforms[0].rect.top + 5
                self.velocity.y = 0

        #collisions check between player and platforms when jumping
        if self.velocity.y < 0: #moving up
            collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False, pygame.sprite.collide_mask)
            if collided_platforms:
                self.velocity.y = 0
                while pygame.sprite.spritecollide(self, self.platform_group, False):
                    self.position.y += 1
                    self.rect.bottomleft = self.position

        #collision check for portals
        if pygame.sprite.spritecollide(self, self.portal_group, False):
            self.portal_sound.play()
            #determine which portal the player should move to
            #first determine left and right
            if self.position.x > WINDOW_WIDTH//2:
                self.position.x = 86
            else:
                self.position.x = WINDOW_WIDTH - 150
            #now determine top and bottom
            if self.position.y > WINDOW_HEIGHT//2:
                self.position.y = 64
            else:
                self.position.y = WINDOW_HEIGHT - 132

    def check_animations(self):
        """check for jump or fire animations"""
        #animate the player jump
        if self.animate_jump:
            if self.velocity.x > 0:
                self.animate(self.jump_right_sprites, 0.1)
            else:
                self.animate(self.jump_left_sprites, 0.1)

        #animate the player fire
        if self.animate_fire:
            if self.velocity.x > 0:
                self.animate(self.attack_right_sprites, 0.25)
            else:
                self.animate(self.attack_left_sprites, 0.25)

    def jump(self):
        """make the player jump if on a platform"""
        #only jump if on a platform
        if pygame.sprite.spritecollide(self, self.platform_group, False):
            self.jump_sound.play()
            self.velocity.y = -1 * self.VERTICAL_JUMP_SPEED
            self.animate_jump = True

    def fire(self):
        """fire a projectile"""
        self.slash_sound.play()
        Bullet(self.rect.centerx, self.rect.centery, self.bullet_group, self)
        self.animate_fire = True

    def reset(self):
        """reset the player's position"""
        self.position = VECTOR(self.starting_x, self.starting_y)
        self.rect.bottomleft = self.position
        self.velocity = VECTOR(0, 0)

    def animate(self, sprite_list, speed):
        """animate the player's actions"""
        if self.current_sprite < len(sprite_list) - 1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0
            #end jump animation
            if self.animate_jump:
                self.animate_jump = False

            #end attack animation
            if self.animate_fire:
                self.animate_fire = False

        self.image = sprite_list[int(self.current_sprite)]

class Portal(pygame.sprite.Sprite):
    """A class that if collided with will teleport you"""

    def __init__(self, x, y, color, portal_group):
        """initialize the portal"""
        super().__init__()

        #create a list for animation frames
        self.portal_sprites = []
        if color == "green": #green portal
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile000.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile001.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile002.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile003.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile004.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile005.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile006.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile007.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile008.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile009.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile010.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile011.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile012.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile013.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile014.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile015.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile016.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile017.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile018.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile019.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile020.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile021.png"), (72,72)))
        else: #purple portal
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile000.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile001.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile002.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile003.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile004.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile005.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile006.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile007.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile008.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile009.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile010.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile011.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile012.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile013.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile014.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile015.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile016.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile017.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile018.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile019.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile020.png"), (72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile021.png"), (72,72)))

        #load an image and get a rect
        self.current_sprite = random.randint(0, len(self.portal_sprites) - 1)
        self.image = self.portal_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        portal_group.add(self)

    def update(self):
        """update the portal"""
        self.animate(self.portal_sprites, 0.2)

    def animate(self, sprite_list, speed):
        """animate the portal"""
        if self.current_sprite < len(sprite_list) - 1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0

        self.image = sprite_list[int(self.current_sprite)]

class Bullet(pygame.sprite.Sprite):
    """A projectile fired by the player"""

    def __init__(self, x, y, bullet_group, player):
        """initialize the bullet"""
        super().__init__()

        #set constant variables
        self.VELOCITY = 20
        self.RANGE = 500

        #load image and get rect
        if player.velocity.x > 0:
            self.image = pygame.transform.scale(pygame.image.load("assets/images/player/slash.png"), (32, 32))
        else:
            self.image = pygame.transform.scale(pygame.transform.flip(
                pygame.image.load("assets/images/player/slash.png"), True, False), (32, 32))
            self.VELOCITY = -1 * self.VELOCITY

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.starting_x = x
        self.starting_y = y

        bullet_group.add(self)

    def update(self):
        """update the bullet"""
        self.rect.x += self.VELOCITY
        #if the bullet has passed the range, kill it
        if abs(self.rect.x - self.starting_x) > self.RANGE:
            self.kill()

class Ruby(pygame.sprite.Sprite):
    """A class the player must collect to earn points and health"""

    def __init__(self, platform_group, portal_group):
        """initialize the ruby"""
        super().__init__()

        #set constant variables
        self.VERTICAL_ACCEL = 3 #gravity
        self.HORIZONTAL_VELOCITY = 5

        #add animation frames
        self.ruby_sprites = []

        self.ruby_sprites = []
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/tile000.png"),
                                                        (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/tile001.png"),
                                                        (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/tile002.png"),
                                                        (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/tile003.png"),
                                                        (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/tile004.png"),
                                                        (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/tile005.png"),
                                                        (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/tile006.png"),
                                                        (64, 64)))
        
        #load image and get rect
        self.current_sprite = 0
        self.image = self.ruby_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (WINDOW_WIDTH//2, 100)

        #attach sprite groups
        self.platform_group = platform_group
        self.portal_group = portal_group

        #load sounds
        self.portal_sound = pygame.mixer.Sound("assets/sounds/portal_sound.wav")
        
        #kinematic vectors
        self.position = VECTOR(self.rect.x, self.rect.y)
        direction = random.choice([-1, 1])
        self.velocity = VECTOR(direction*self.HORIZONTAL_VELOCITY, 0)
        self.accel = VECTOR(0, self.VERTICAL_ACCEL)

    def update(self):
        """update the ruby"""
        self.animate(self.ruby_sprites, 0.25)
        self.move()
        self.check_collisions()

    def move(self):
        """move the ruby"""
        #the accel doesn't change, so we don't need to update the accel vector
        #calculate new kinematics values
        self.velocity += self.accel
        self.position += self.velocity + 0.5*self.accel

        #update rect based on new kinematics values and add wrap-around movement
        if self.position.x < 0:
            self.position.x = WINDOW_WIDTH
        elif self.position.x > WINDOW_WIDTH:
            self.position.x = 0

        self.rect.bottomleft = self.position

    def check_collisions(self):
        """check for collisions with platforms and portals"""
        #collision check between ruby and platforms when falling
        collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False)
        if collided_platforms:
            self.position.y = collided_platforms[0].rect.top + 1
            self.velocity.y = 0

        #collision check for portals
        if pygame.sprite.spritecollide(self, self.portal_group, False):
            self.portal_sound.play()
            #determine which portal the ruby should move to
            #first determine left and right
            if self.position.x > WINDOW_WIDTH//2:
                self.position.x = 86
            else:
                self.position.x = WINDOW_WIDTH - 150
            #now determine top and bottom
            if self.position.y > WINDOW_HEIGHT//2:
                self.position.y = 64
            else:
                self.position.y = WINDOW_HEIGHT - 132


    def animate(self, sprite_list, speed):
        """Animate the ruby"""
        if self.current_sprite < len(sprite_list) - 1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0

        self.image = sprite_list[int(self.current_sprite)]

class RubyMaker(pygame.sprite.Sprite):
    """A tile that is animated. A ruby will be generated here"""

    def __init__(self, x, y, main_group):
        """initialize the ruby maker"""
        super().__init__()

        #load animation frames
        self.ruby_sprites = []
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/tile000.png"),
                                                        (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/tile001.png"),
                                                        (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/tile002.png"),
                                                        (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/tile003.png"),
                                                        (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/tile004.png"),
                                                        (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/tile005.png"),
                                                        (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/tile006.png"),
                                                        (64, 64)))

        #load image and get rect
        self.current_sprite = 0
        self.image = self.ruby_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        #add to the main group
        main_group.add(self)


    def update(self):
        """update the ruby maker"""
        self.animate(self.ruby_sprites, .25)

    def animate(self, sprite_list, speed):
        """animate the ruby maker"""
        if self.current_sprite < len(sprite_list) - 1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0

        self.image = sprite_list[int(self.current_sprite)]

class Tile(pygame.sprite.Sprite):
    """A class to represent a tile in the display"""

    def __init__(self, x, y, image_int, main_group, sub_group=None):
        """create the tile"""
        super().__init__()
        #load in image and add it to the subgroup
        if image_int == 1: #dirt image
            self.image = pygame.transform.scale(pygame.image.load("assets/images/tiles/Tile (1).png"), (32, 32))
        elif image_int == 2: #ground platform
            self.image = pygame.transform.scale(pygame.image.load("assets/images/tiles/Tile (2).png"), (32, 32))
            sub_group.add(self)
        elif image_int == 3: #left platform
            self.image = pygame.transform.scale(pygame.image.load("assets/images/tiles/Tile (3).png"), (32, 32))
            sub_group.add(self)
        elif image_int == 4: #middle platform
            self.image = pygame.transform.scale(pygame.image.load("assets/images/tiles/Tile (4).png"), (32, 32))
            sub_group.add(self)
        elif image_int == 5: #right platform
            self.image = pygame.transform.scale(pygame.image.load("assets/images/tiles/Tile (5).png"), (32, 32))
            sub_group.add(self)

        #add every tile to main group
        main_group.add(self)

        #get the rect and position in the display surface
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        #create mask
        self.mask = pygame.mask.from_surface(self.image)

class Zombie(pygame.sprite.Sprite):
    """an enemy class that moves across the screen"""

    def __init__(self, platform_group, portal_group, min_speed, max_speed):
        """initialize the zombie"""
        super().__init__()

        #set constant variables
        self.VERTICAL_ACCEL = 3 #gravity
        self.RISE_TIME = 2

        #create animation frames
        self.walk_right_sprites = []
        self.walk_left_sprites = []
        self.die_right_sprites = []
        self.die_left_sprites = []
        self.rise_right_sprites = []
        self.rise_left_sprites = []

        gender = random.randint(0, 1)
        if gender == 0:
            #walking
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/walk/Walk (1).png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/walk/Walk (2).png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/walk/Walk (3).png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/walk/Walk (4).png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/walk/Walk (5).png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/walk/Walk (6).png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/walk/Walk (7).png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/walk/Walk (8).png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/walk/Walk (9).png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/walk/Walk (10).png"), (64, 64)))
            for sprite in self.walk_right_sprites:
                self.walk_left_sprites.append(pygame.transform.flip(sprite, True, False))
            #dying
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (1).png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (2).png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (3).png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (4).png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (5).png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (6).png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (7).png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (8).png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (9).png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (10).png"), (64, 64)))
            for sprite in self.die_right_sprites:
                self.die_left_sprites.append(pygame.transform.flip(sprite, True, False))
            #rising
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (10).png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (9).png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (8).png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (7).png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (6).png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (5).png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (4).png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (3).png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (2).png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (1).png"), (64, 64)))
            for sprite in self.rise_right_sprites:
                self.rise_left_sprites.append(pygame.transform.flip(sprite, True, False))
        else:
            #walking
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/walk/Walk (1).png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/walk/Walk (2).png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/walk/Walk (3).png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/walk/Walk (4).png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/walk/Walk (5).png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/walk/Walk (6).png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/walk/Walk (7).png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/walk/Walk (8).png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/walk/Walk (9).png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/walk/Walk (10).png"), (64, 64)))
            for sprite in self.walk_right_sprites:
                self.walk_left_sprites.append(pygame.transform.flip(sprite, True, False))
            #dying
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (1).png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (2).png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (3).png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (4).png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (5).png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (6).png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (7).png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (8).png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (9).png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (10).png"), (64, 64)))
            for sprite in self.die_right_sprites:
                self.die_left_sprites.append(pygame.transform.flip(sprite, True, False))
            #rising
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (10).png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (9).png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (8).png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (7).png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (6).png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (5).png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (4).png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (3).png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (2).png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (1).png"), (64, 64)))
            for sprite in self.rise_right_sprites:
                self.rise_left_sprites.append(pygame.transform.flip(sprite, True, False))

        #load an image and get rect
        self.direction = random.choice([-1, 1])

        self.current_sprite = 0
        if self.direction == -1:
            self.image = self.walk_left_sprites[self.current_sprite]
        else:
            self.image = self.walk_right_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (random.randint(100, WINDOW_WIDTH - 100), -100)

        #attach sprite groups
        self.platform_group = platform_group
        self.portal_group = portal_group

        #animation booleans
        self.animate_death = False
        self.animate_rise = False

        #load sounds
        self.hit_sound = pygame.mixer.Sound("assets/sounds/zombie_hit.wav")
        self.kick_sound = pygame.mixer.Sound("assets/sounds/zombie_kick.wav")
        self.portal_sound = pygame.mixer.Sound("assets/sounds/portal_sound.wav")

        #load in kinematics vectors
        self.position = VECTOR(self.rect.x, self.rect.y)
        self.velocity = VECTOR(self.direction * random.randint(min_speed, max_speed), 0)
        self.accel = VECTOR(0, self.VERTICAL_ACCEL)

        #set initial values
        self.is_dead = False
        self.round_time = 0
        self.frame_count = 0


    def update(self):
        """update the zombie"""
        self.move()
        self.check_collisions()
        self.check_animations()

        #determine when the zombie should rise from the dead
        if self.is_dead:
            self.frame_count += 1
            if self.frame_count % FPS == 0:
                self.round_time += 1
                if self.round_time == self.RISE_TIME:
                    self.animate_rise = True
                    #when the zombie died, the image was kept at the last image
                    #when it rises we want to start at index 0 of the rise_sprites list
                    self.current_sprite = 0

    def move(self):
        """move the zombie"""
        if not self.is_dead:
            #animate the zombie walking
            if self.direction == -1:
                self.animate(self.walk_left_sprites, 0.5)
            else:
                self.animate(self.walk_right_sprites, 0.5)

            #the accel doesn't change, so we don't need to update the accel vector
            #calculate new kinematics values
            self.velocity += self.accel
            self.position += self.velocity + 0.5*self.accel

            #update rect based on new kinematics values and add wrap-around movement
            if self.position.x < 0:
                self.position.x = WINDOW_WIDTH
            elif self.position.x > WINDOW_WIDTH:
                self.position.x = 0

            self.rect.bottomleft = self.position

    def check_collisions(self):
        """checks for collisions with platforms and portals"""
        #collision check between player and zombie when falling
        collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False)
        if collided_platforms:
            self.position.y = collided_platforms[0].rect.top + 1
            self.velocity.y = 0

        #collision check for portals
        if pygame.sprite.spritecollide(self, self.portal_group, False):
            self.portal_sound.play()
            #determine which portal the zombie should move to
            #first determine left and right
            if self.position.x > WINDOW_WIDTH//2:
                self.position.x = 86
            else:
                self.position.x = WINDOW_WIDTH - 150
            #now determine top and bottom
            if self.position.y > WINDOW_HEIGHT//2:
                self.position.y = 64
            else:
                self.position.y = WINDOW_HEIGHT - 132

    def check_animations(self):
        """check for death animation"""
        #animate the zombie death
        if self.animate_death:
            if self.direction == 1:
                self.animate(self.die_right_sprites, .095)
            else:
                self.animate(self.die_left_sprites, .095)

        #animate the zombie rise
        if self.animate_rise:
            if self.direction == 1:
                self.animate(self.rise_right_sprites, .095)
            else:
                self.animate(self.rise_left_sprites, .095)
        

    def animate(self, sprite_list, speed):
        """animate the zombie's actions"""
        if self.current_sprite < len(sprite_list) - 1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0

            #end death animation
            if self.animate_death:
                self.current_sprite = len(sprite_list) - 1
                self.animate_death = False

            #end rise animation
            if self.animate_rise:
                self.animate_rise = False
                self.is_dead = False
                self.frame_count = 0
                self.round_time = 0

        self.image = sprite_list[int(self.current_sprite)]

#Create Sprite Groups
my_main_tile_group = pygame.sprite.Group()
my_platform_group = pygame.sprite.Group()

my_player_group = pygame.sprite.Group()
my_bullet_group = pygame.sprite.Group()

my_zombie_group = pygame.sprite.Group()

my_portal_group = pygame.sprite.Group()
my_ruby_group = pygame.sprite.Group()

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
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
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
            Tile(j * 32, i * 32, 1, my_main_tile_group)
        #ground platform tile
        elif tile_map[i][j] == 2:
            Tile(j * 32, i * 32, 2, my_main_tile_group, my_platform_group)
        #left platform tile
        elif tile_map[i][j] == 3:
            Tile(j * 32, i * 32, 3, my_main_tile_group, my_platform_group)
        #middle platform tile
        elif tile_map[i][j] == 4:
            Tile(j * 32, i * 32, 4, my_main_tile_group, my_platform_group)
        #right platform tile
        elif tile_map[i][j] == 5:
            Tile(j * 32, i * 32, 5, my_main_tile_group, my_platform_group)
        #ruby maker
        elif tile_map[i][j] == 6:
            RubyMaker(j * 32, i * 32, my_main_tile_group)
        #portals
        elif tile_map[i][j] == 7:
            Portal(j * 32, i * 32, "green", my_portal_group)
        elif tile_map[i][j] == 8:
            Portal(j * 32, i * 32, "purple", my_portal_group)
        #player
        elif tile_map[i][j] == 9:
            my_player = Player(j * 32 - 32, i * 32 + 32, my_platform_group, my_portal_group, my_bullet_group)
            my_player_group.add(my_player)


#Load in background image
background_image = pygame.transform.scale(pygame.image.load("assets/images/background.png"),
                                          (WINDOW_WIDTH, WINDOW_HEIGHT))
background_rect = background_image.get_rect()
background_rect.topleft = (0,0)

#create a game
my_game = Game(my_player, my_zombie_group, my_platform_group, my_portal_group, my_bullet_group, my_ruby_group)
my_game.pause_game("Zombie Knight!", "Press 'Enter' to begin", "v1.0.1")
pygame.mixer.music.play(-1, 0.0)

"""MAIN GAME LOOP"""
running = True
while running:
    #Check to see if user wants to quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                my_player.jump()
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                my_player.fire()

            # #rain zombies DEBUG
            # elif event.key == pygame.K_RETURN:
            #     my_zombie_group.add(Zombie(my_platform_group, my_portal_group, 2, 7))

    #blit the background
    DISPLAY_SURFACE.blit(background_image, background_rect)

    #draw our tiles
    my_main_tile_group.update()
    my_main_tile_group.draw(DISPLAY_SURFACE)

    #draw and update sprite groups
    my_portal_group.update()
    my_portal_group.draw(DISPLAY_SURFACE)

    my_player_group.update()
    my_player_group.draw(DISPLAY_SURFACE)

    my_bullet_group.update()
    my_bullet_group.draw(DISPLAY_SURFACE)

    my_zombie_group.update()
    my_zombie_group.draw(DISPLAY_SURFACE)

    my_ruby_group.update()
    my_ruby_group.draw(DISPLAY_SURFACE)

    #update and draw game
    my_game.update()
    my_game.draw()

    #update display and tick clock
    pygame.display.update()
    CLOCK.tick(FPS)

#end the game
pygame.quit()
