import pygame
from GameObject import GameObject


class TestObj(GameObject):
    def __init__(self, game):
        super().__init__(game)
        self.cell_size = 100

        self.x = 0
        self.y = 0

    def draw(self):
        cam = self.game.camera
        fov = cam.fov

        scale = max(0.1, 1.0 + (fov * 0.1))
        zoomed_cell_size = self.cell_size * scale

        screen_center_x = self.game.surface.get_width() // 2
        screen_center_y = self.game.surface.get_height() // 2


        for i in range(10):
            for j in range(10):
                world_x = self.x + i * self.cell_size
                world_y = self.y + j * self.cell_size

                draw_x = (world_x - cam.x) * scale + screen_center_x
                draw_y = (world_y - cam.y) * scale + screen_center_y

                pygame.draw.rect(self.game.surface, (200, 200, 200), (
                    draw_x,
                    draw_y,
                    zoomed_cell_size,
                    zoomed_cell_size
                ), 2)

    def update(self):
        pass