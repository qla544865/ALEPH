import pygame
from GameObject import GameObject


class MarqueeSelection(GameObject):
    def __init__(self, game):
        super().__init__(game)
        
        self.is_selecting = False
        self.selection_start = (0, 0)
        self.selection_end = (0, 0)
        self.selected_objects = []


    def update(self):
        self.selected_objects.clear()
                
        min_x = min(self.selection_start[0], self.selection_end[0])
        min_y = min(self.selection_start[1], self.selection_end[1])
        width = abs(self.selection_start[0] - self.selection_end[0])
        height = abs(self.selection_start[1] - self.selection_end[1])
        selection_rect = pygame.Rect(min_x, min_y, width, height)

        camera = self.game.camera
        scale = max(0.1, 1.0 + (camera.fov * 0.1))
        screen_center_x = self.game.surface.get_width() // 2
        screen_center_y = self.game.surface.get_height() // 2

        for obj in self.game.objects:
            draw_x = (obj.x - camera.x) * scale + screen_center_x
            draw_y = (obj.y - camera.y) * scale + screen_center_y
            
            # zoomed_size = obj.size * scale 
            # obj_rect = pygame.Rect(draw_x, draw_y, zoomed_size, zoomed_size)

            if selection_rect.collidepoint(draw_x, draw_y):
                self.selected_objects.append(obj)
                obj.is_selected = True
            else:
                obj.is_selected = False

    def draw(self):
        
        if self.is_selecting:
            self.selection_end = pygame.mouse.get_pos()
            
            min_x = min(self.selection_start[0], self.selection_end[0])
            min_y = min(self.selection_start[1], self.selection_end[1])
            width = abs(self.selection_start[0] - self.selection_end[0])
            height = abs(self.selection_start[1] - self.selection_end[1])
            
            selection_rect = pygame.Rect(min_x, min_y, width, height)
            
            pygame.draw.rect(self.game.surface, (100, 255, 100), selection_rect, 5)