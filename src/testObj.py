import pygame
from GameObject import GameObject
from Event import Event


class TestObj(GameObject):
    def __init__(self, game):
        super().__init__(game)
        self.size = 100

        self.x = 0
        self.y = 0

    def draw(self):
        cam = self.game.camera
        fov = cam.fov

        scale = max(0.1, 1.0 + (fov * 0.1))
        zoomed_cell_size = self.size * scale

        screen_center_x = self.game.surface.get_width() // 2
        screen_center_y = self.game.surface.get_height() // 2


        for i in range(-10,11):
            for j in range(-10,11):
                world_x = self.x + i * self.size
                world_y = self.y + j * self.size

                draw_x = (world_x - cam.x) * scale + screen_center_x
                draw_y = (world_y - cam.y) * scale + screen_center_y

                pygame.draw.rect(self.game.surface, (150, 150, 150), (
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

        self.test_event = Event(game, pygame.MOUSEMOTION, self.onMouseButtonDown)

    def onMouseButtonDown(self, event):
        # if event.button == 1:
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

