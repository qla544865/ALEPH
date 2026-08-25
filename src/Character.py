import pygame
from GameObject import GameObject


class Character(GameObject):
    def __init__(self, game):
        super().__init__(game)
        self.size = 100

        self.x = 0
        self.y = 0

        self.model = game.AssetManager.image_scaled("Character/don_quixote", (self.size, self.size))

        self.is_selected = False

    def draw(self):
        self.drawModel()
        color = (200,200,200) if not self.is_selected else (100,250,100)

        self.drawRect(color, self.size, border_width=5)

    def update(self):
        pass