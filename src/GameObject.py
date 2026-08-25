import pygame

class GameObject:
    def __init__(self, game):
        self.x = 0
        self.y = 0

        self.game = game

        self.screen_width = self.game.surface.get_width()
        self.screen_height = self.game.surface.get_height()

        self.screen_center_x = self.screen_width // 2
        self.screen_center_y = self.screen_height // 2

        self.model: pygame.Surface = None

        self.size = 0

    def getPositionOnScreen(self):
        camera = self.game.camera
        fov = camera.fov

        scale = max(0.1, 1.0 + (fov * 0.1))

        world_x = self.x
        world_y = self.y

        draw_x = (world_x - camera.x) * scale + self.screen_center_x
        draw_y = (world_y - camera.y) * scale + self.screen_center_y

        return draw_x, draw_y

    def getSizeScaleOnScreen(self):
        camera = self.game.camera
        fov = camera.fov

        scale = max(0.1, 1.0 + (fov * 0.1))
        return scale

    def drawModel(self):
        if self.model is None:
            return

        scale = self.getSizeScaleOnScreen()
        screen_x, screen_y = self.getPositionOnScreen()

        scaled_width = int(self.model.get_width() * scale)
        scaled_height = int(self.model.get_height() * scale)

        if scaled_width <= 0 or scaled_height <= 0:
            return

        scaled_model = pygame.transform.smoothscale(self.model, (scaled_width, scaled_height)) if scale >= 1 else pygame.transform.scale(self.model, (scaled_width, scaled_height))

        blit_x = screen_x
        blit_y = screen_y

        self.game.surface.blit(scaled_model, (blit_x, blit_y))

    def drawRect(self, color, size, offset=(0,0), border_width=-1):
        if isinstance(size, (int, float)):
            size = [size, size]
        if isinstance(offset, (int, float)):
            offset = [offset, offset]
                        
        typeof_size = type(size)

        sizeScale = self.getSizeScaleOnScreen()

        scaled_size_x = size[0] * sizeScale
        scaled_size_y = size[1] * sizeScale
        

        draw_x, draw_y = self.getPositionOnScreen()


        pygame.draw.rect(self.game.surface, color, (
            draw_x + offset[0],
            draw_y + offset[1],
            scaled_size_x,
            scaled_size_y
        ), border_width)

    def draw(self):
        """ Use camera in game to draw object """
        pass

    def update(self):
        """ Update Every Frame """
        pass

