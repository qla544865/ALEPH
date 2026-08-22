import pygame
from Camera import Camera
from GameObject import GameObject
from testObj import TestObj
from Event import *
from Selection import MarqueeSelection
from AssetManager import AssetManager


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720


class Game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.running = True

        self.keyPressed = []
        self.dt = 0

        self.event = None
        self.scrolling = 0
        self.mouseButtonDown = 0
        self.mouseRel = [0,0]
        self.mouseClickPosition = (0,0)
        self.eventManager = EventManager(self)

        self.eventManager.addEvent(Event(self, pygame.QUIT, self.onQuit))

        self.clock = pygame.time.Clock()

        self.camera = Camera(self)
        self.selection = MarqueeSelection(self)

        testObj = TestObj(self)

        self.AssetManager = AssetManager(self)

        self.objects = [testObj]

        self.fps = 60

    
    def onQuit(self, event):
        self.running=False

    def gameLoop(self):
        while self.running:
            self.dt = self.clock.tick(self.fps) / 1000.0
            self.eventHandle()
            self.update()
            self.draw()

        self.quit()

    def quit(self):
        pygame.quit()

    def eventHandle(self):
        self.scrolling = 0
        self.mouseButtonDown = 0
        for event in pygame.event.get():
            self.eventManager.update(event)
            if event.type == pygame.MOUSEWHEEL:
                self.scrolling = event.y
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.selection.is_selecting = True
                    self.selection.selection_start = pygame.mouse.get_pos()
                    self.selection.selection_end = self.selection.selection_start
                elif event.button == 3:
                    self.mouseButtonDown = event.button
                    self.mouseClickPosition = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.selection.is_selecting = False
                    self.selection.update()
                elif event.button == 3:
                    self.mouseButtonDown = 0

    


    def update(self):
        self.keyPressed = pygame.key.get_pressed()

        self.camera.update()

        for obj in self.objects:
            obj.update()

        

    def draw(self):
        self.surface.fill((10, 10, 50))
        
        for obj in self.objects:
            obj.draw()

        self.selection.draw()


        pygame.display.update()



if __name__ == "__main__":
    window = Game()
    window.gameLoop()