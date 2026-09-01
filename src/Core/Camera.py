import pygame
from Core.GameObject import GameObject

class Camera(GameObject):
    def __init__(self, game):
        super().__init__(game)
        self.x = 0
        self.y = 0

        self.fov = 0
        self.mx_fov = 8

        self.mouse_rel = None
        self.prev_cam_pos = None
        self.controlled_by_script = True

    def onChangeFov(self):
        if self.fov < -self.mx_fov:
            self.fov = -self.mx_fov
        elif self.fov > self.mx_fov:
            self.fov = self.mx_fov

    def getWorldMousePos(self):
        mx, my = pygame.mouse.get_pos()
        scale = max(0.1, 1.0 + (self.fov * 0.1))

        world_x = (mx - self.screen_center_x) / scale + self.x
        world_y = (my - self.screen_center_y) / scale + self.y

        return world_x, world_y
