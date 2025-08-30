import pygame

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
