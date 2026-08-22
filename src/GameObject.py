class GameObject:
    def __init__(self, game):
        self.x = 0
        self.y = 0

        self.game = game

    def getScreenPosition(self):
        camera = self.game.camera

        return (self.x - camera.x/2, self.y - camera.y/2)

    def draw(self):
        """ Use camera in game to draw object """
        pass

    def update(self):
        """ Update Every Frame """
        pass

