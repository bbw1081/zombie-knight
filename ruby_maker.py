import pygame

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

