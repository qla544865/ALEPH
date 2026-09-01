import pygame
from Core.GameObject import GameObject
from Core.Event import Event


class TestObj(GameObject):
    def __init__(self, game):
        super().__init__(game)
        self.size = 100

        self.x = 0
        self.y = 0

        # grid bounds (world units)
        self._grid_min = -3
        self._grid_max = 3

    def draw(self):
        cam = self.game.camera
        fov = cam.fov

        scale = max(0.1, 1.0 + (fov * 0.1))
        zoomed_cell_size = self.size * scale

        sw = self.screen_width
        sh = self.screen_height
        screen_center_x = sw // 2
        screen_center_y = sh // 2

        # Compute visible world-space range from camera viewport
        inv_scale = 1.0 / scale
        world_left   = cam.x - screen_center_x * inv_scale
        world_right  = cam.x + (sw - screen_center_x) * inv_scale
        world_top    = cam.y - screen_center_y * inv_scale
        world_bottom = cam.y + (sh - screen_center_y) * inv_scale

        # Convert to grid indices (clamped to grid bounds)
        import math
        i_min = max(self._grid_min, math.floor((world_left  - self.x) / self.size) - 1)
        i_max = min(self._grid_max, math.ceil( (world_right - self.x) / self.size))
        j_min = max(self._grid_min, math.floor((world_top    - self.y) / self.size) - 1)
        j_max = min(self._grid_max, math.ceil( (world_bottom - self.y) / self.size))

        surface = self.game.surface
        color = (150, 150, 150)

        for i in range(i_min, i_max + 1):
            for j in range(j_min, j_max + 1):
                world_x = self.x + i * self.size
                world_y = self.y + j * self.size

                draw_x = (world_x - cam.x) * scale + screen_center_x
                draw_y = (world_y - cam.y) * scale + screen_center_y

                pygame.draw.rect(surface, color, (
                    draw_x,
                    draw_y,
                    zoomed_cell_size,
                    zoomed_cell_size
                ), 2)

    def update(self):
        pass


class TestMouse(GameObject):
    def __init__(self, game):
        super().__init__(game)
        self.size = 5

        self.x = 0
        self.y = 0

        self.test_event = Event(game, pygame.MOUSEMOTION, self.onMouseMove)

    def onMouseMove(self, event):
        self.x,self.y = self.game.camera.getWorldMousePos()

    def draw(self):
        size = self.size * self.getSizeScaleOnScreen()

        draw_x, draw_y = self.getPositionOnScreen()

        pygame.draw.circle(self.game.surface, (255, 255, 255), (
            draw_x,
            draw_y,
        ),  size)

    def update(self):
        pass

