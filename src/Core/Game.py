import pygame
from Core.Camera import Camera
from Core.GameObject import GameObject
from Core.Character import Character
from Core.Item import GameItem
from Core.testObj import *
from Core.Event import *
from Core.Selection import MarqueeSelection
from Core.AssetManager import AssetManager
from Core.ScriptLoader import ScriptLoader


DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720


class Game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode(
            (DEFAULT_WIDTH, DEFAULT_HEIGHT), pygame.RESIZABLE
        )
        self.project_name = "ALEPH - DEV"
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

        self.AssetManager = AssetManager(self)

        self.ScriptLoader = ScriptLoader(self)

        self.clock = pygame.time.Clock()

        self.fps = 120

        # --- Loading screen ---
        self._load_assets()

    # ------------------------------------------------------------------
    # Loading screen
    # ------------------------------------------------------------------

    def _draw_loading_screen(self, progress: float, label: str = ""):
        """Render a loading bar.  *progress* is 0.0 – 1.0."""
        w = self.surface.get_width()
        h = self.surface.get_height()

        self.surface.fill((10, 10, 50))

        # Title
        title_font = pygame.font.Font(None, 48)
        title_surf = title_font.render(self.project_name, True, (220, 220, 255))
        self.surface.blit(
            title_surf,
            (w // 2 - title_surf.get_width() // 2, h // 2 - 80),
        )

        # Progress bar background
        bar_w, bar_h = 400, 20
        bar_x = w // 2 - bar_w // 2
        bar_y = h // 2
        pygame.draw.rect(self.surface, (60, 60, 80), (bar_x, bar_y, bar_w, bar_h))

        # Progress bar fill
        fill_w = int(bar_w * max(0.0, min(1.0, progress)))
        if fill_w > 0:
            pygame.draw.rect(
                self.surface, (100, 200, 255), (bar_x, bar_y, fill_w, bar_h)
            )

        # Progress bar border
        pygame.draw.rect(
            self.surface, (150, 150, 180), (bar_x, bar_y, bar_w, bar_h), 2
        )

        # Label
        if label:
            label_font = pygame.font.Font(None, 24)
            label_surf = label_font.render(label, True, (180, 180, 200))
            self.surface.blit(
                label_surf,
                (w // 2 - label_surf.get_width() // 2, bar_y + bar_h + 12),
            )

        # Percentage
        pct_font = pygame.font.Font(None, 22)
        pct_surf = pct_font.render(f"{int(progress * 100)}%", True, (200, 200, 220))
        self.surface.blit(
            pct_surf,
            (w // 2 - pct_surf.get_width() // 2, bar_y - 24),
        )

        pygame.display.flip()

    def _load_assets(self):
        """Initialise game objects while showing a loading bar."""

        # Define loading steps as (label, callable) pairs.
        # Each callable performs one chunk of initialisation work.
        steps: list[tuple[str, callable]] = []

        # -- Core subsystems (lightweight but still good to show) ----------
        steps.append(("Initialising camera…", lambda: setattr(self, 'camera', Camera(self))))
        steps.append(("Initialising selection…", lambda: setattr(self, 'selection', MarqueeSelection(self))))

        # -- Placeholder lists so lambdas below can append ------------------
        self.objects = []
        self.characters = []

        steps.append(("Loading scripts...", self.ScriptLoader.load_all))
        steps.append(("Loading grid...", self._load_grid))
        steps.append(("Loading character assets...", self._load_character))
        steps.append(("Loading cursor...", self._load_mouse))

        total = len(steps)
        for i, (label, fn) in enumerate(steps):
            # Pump events so the OS doesn't think the window is frozen
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                elif event.type == pygame.VIDEORESIZE:
                    self.surface = pygame.display.set_mode(
                        (event.w, event.h), pygame.RESIZABLE
                    )

            self._draw_loading_screen(i / total, label)
            fn()

        # Final 100 %
        self._draw_loading_screen(1.0, "Done!")
        pygame.time.wait(10)

    def _load_grid(self):
        testObj = TestObj(self)
        self.objects.append(testObj)

    def _load_character(self):
        testChar = Character(self)
        self.objects.append(testChar)
        self.characters.append(testChar)

        testKhoGa = GameItem(self)
        testKhoGa.x = 0
        testKhoGa.y = -150
        self.objects.append(testKhoGa)

    def _load_mouse(self):
        testMouse = TestMouse(self)
        self.objects.append(testMouse)
        self.eventManager.addEvent(testMouse.test_event)

    
    def onQuit(self, event):
        self.running=False

    def gameLoop(self):
        while self.running:
            self.dt = self.clock.tick(self.fps) / 1000.0
            self.eventHandle()
            self.update()
            self.draw()

            pygame.display.set_caption(f"Game - {int(self.clock.get_fps())}")

        self.quit()

    def quit(self):
        pygame.quit()

    def eventHandle(self):
        self.scrolling = 0
        self.mouseButtonDown = 0
        for event in pygame.event.get():
            self.eventManager.update(event)
            if event.type == pygame.VIDEORESIZE:
                self.surface = pygame.display.set_mode(
                    (event.w, event.h), pygame.RESIZABLE
                )
            elif event.type == pygame.MOUSEWHEEL:
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

        self.ScriptLoader.update(self.dt)


    def draw(self):
        self.surface.fill((10, 10, 50))
        
        for obj in self.objects:
            obj.draw()

        self.selection.draw()


        pygame.display.update()



if __name__ == "__main__":
    window = Game()
    window.gameLoop()