import pygame

class Event:
    """
    - `game`: Game
    - `eventType`: pygame event
    - `callback`: callback

    Callback Eg:
    ```
    def OnPress(self: Game, event):
        print(event.key)
    
    game.EventManager.addEvent(Event(game, pygame.KEYDOWN, OnPress))
    ```
    """
    def __init__(self, game, eventType, callback):
        self.game = game
        self.eventType = eventType
        self.callback = callback


class EventManager:
    def __init__(self, game):
        self.game = game
        self.events:dict[int, list] = {}

    def addEvent(self, event:Event):
        eventType = event.eventType
        try:
            self.events[eventType].append(event)
        except KeyError:
            self.events[eventType] = [event]
    
    def update(self, event):
        try:
            for e in self.events[event.type]:
                e.callback(event)
        except KeyError:
            self.events[event.type] = []

