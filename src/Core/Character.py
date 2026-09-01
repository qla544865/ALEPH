import pygame
from Core.GameObject import GameObject


class Character(GameObject):
    def __init__(self, game):
        super().__init__(game)
        self.w = 1227 # sprite width
        self.h = 554 # sprite height

        self.size = (100,100)


        self.x = 0
        self.y = 0

        self.model = game.AssetManager.image_scaled("Character/don_quixote", self.size)

        self.is_selected = False

        self.sprite = self.game.AssetManager.animated_sprite(
            "Character/la_manchaland_sprite",
            cols=10,
            rows=6,
            fps=24.0,
            scale_size=self.size
        )

    def draw(self):
        self.drawModel()
        color = (200,200,200) if not self.is_selected else (100,250,100)

        scale = self.getSizeScaleOnScreen()
        sx, sy = self.getPositionOnScreen()
        sw = int(self.w * scale)
        sh = int(self.h * scale)
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