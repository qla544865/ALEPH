import pygame
from Core.GameObject import GameObject


class GameItem(GameObject):
    def __init__(self, game):
        super().__init__(game)

        self.size = (80, 120)


        self.x = 0
        self.y = 0

        self.model = game.AssetManager.image_scaled("Items/khoga", self.size)

        self.is_selected = False

    def draw(self):
        self.drawModel()
        color = (200,200,200) if not self.is_selected else (100,250,100)

        scale = self.getSizeScaleOnScreen()
        sx, sy = self.getPositionOnScreen()
        sw = int(300 * scale)
        sh = int(600 * scale)
        if self.isOnScreen(sx, sy, sw, sh):
            self.drawRect(color, self.size, border_width=5)

    def update(self):
        pass

    def updateSprite(self):
        self.sprite.update(self.game.dt)
        self.model = self.sprite.current_frame
        self.update_lod()
        
        if self.current_lod_sprite:
            self.current_lod_sprite.update(self.game.dt)
            self.model = self.current_lod_sprite.current_frame