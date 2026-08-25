import pygame
from GameObject import GameObject

class Camera(GameObject):
    def __init__(self, game):
        super().__init__(game)
        self.x = 0
        self.y = 0

        self.fov = 0
        self.mx_fov = 8

        self.mouse_rel = None
        self.prev_cam_pos = None

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


    def update(self):
        keyPress = self.game.keyPressed
        dt = self.game.dt
        scale = max(0.1, 1.0 + (self.fov * 0.1))
        speed = 300*1/scale
        zoom_speed = 8

        if keyPress[pygame.K_w]:
            self.y -= speed * dt
        if keyPress[pygame.K_s]:
            self.y += speed * dt
        if keyPress[pygame.K_a]:
            self.x -= speed * dt
        if keyPress[pygame.K_d]:
            self.x += speed * dt


        mouse_pressed = pygame.mouse.get_pressed()

        if mouse_pressed[2]:
            mouse_pos = pygame.mouse.get_pos()
            if not self.prev_cam_pos:
                self.prev_cam_pos = (self.x, self.y)
            else:
                self.mouse_rel = (
                    self.game.mouseClickPosition[0] - mouse_pos[0],
                    self.game.mouseClickPosition[1] - mouse_pos[1]
                )
                self.x = self.prev_cam_pos[0] + (self.mouse_rel[0]/scale)
                self.y = self.prev_cam_pos[1] + (self.mouse_rel[1]/scale)
        else:
            self.prev_cam_pos = None
            self.mouse_rel = None



        


        if keyPress[pygame.K_MINUS]:
            self.fov -= zoom_speed * dt
            self.onChangeFov()
        if keyPress[pygame.K_EQUALS]:
            self.fov += zoom_speed * dt
            self.onChangeFov()
        if self.game.scrolling < 0:
            self.fov -= zoom_speed * dt * 5
            self.onChangeFov()
        if self.game.scrolling > 0:
            self.fov += zoom_speed * dt * 5
            self.onChangeFov()