# ALEPH

A 2D game framework built on **pygame**, featuring a zoomable/pannable camera, marquee selection, event dispatching, and a centralised asset manager.

> **Python 3.10.1** · **pygame 2.6.1**

---

## Quick Start

```bash
# Create & activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # PowerShell
# .\.venv\Scripts\activate.bat      # CMD

# Install dependencies
pip install -r requirements.txt

# Run
cd src
python main.py
```

---

## Project Structure

```
ALEPH/
├── Asset/
│   ├── Audio/              # SFX & music
│   └── Character/          # Sprites
│       └── don_quixote.png
├── src/
│   ├── main.py             # Entry point
│   ├── Game.py             # Game loop & subsystem wiring
│   ├── GameObject.py       # Base class — position, drawing helpers
│   ├── Camera.py           # Pan & zoom camera + world↔screen conversion
│   ├── Selection.py        # Marquee (rubber-band) selection
│   ├── Event.py            # Event dispatcher
│   ├── AssetManager.py     # Lazy-loading asset cache
│   ├── Character.py        # Character entity (sprite + selection)
│   └── testObj.py          # TestObj (debug grid) & TestMouse (cursor dot)
├── .gitignore
└── requirements.txt
```

---

## Architecture

```
main.py  →  Game
              ├── Camera            (extends GameObject)
              ├── MarqueeSelection  (extends GameObject)
              ├── EventManager      (dispatches Event callbacks)
              ├── AssetManager      (images, SFX, music, fonts)
              ├── objects[]         (TestObj, Character, TestMouse, ...)
              └── characters[]      (selectable Character instances)
```

**Frame loop** — every tick:

```
eventHandle()  →  update()  →  draw()
```

The window title shows the live FPS counter. Target framerate is **120**.

See [Documentation.md](Documentation.md) for the full per-class API reference.

---

## Controls

| Input | Action |
|---|---|
| `W / A / S / D` | Pan camera |
| `+` / `-` | Zoom in / out |
| Mouse wheel | Zoom in / out (5× speed) |
| Right-click drag | Pan camera |
| Left-click drag | Marquee select |
| Left-click (no drag) | Toggle select on single character |

---

## Key Concepts

### GameObject Drawing Helpers

All entities extend `GameObject`, which provides built-in drawing methods so
subclasses don't need to manually compute camera projection:

```python
self.drawModel()                                        # draw self.model (sprite) with camera transform
self.drawRect(color, size, offset=(0,0), border_width)  # draw a rect at world position + offset
pos = self.getPositionOnScreen()                        # (screen_x, screen_y)
scale = self.getSizeScaleOnScreen()                     # current zoom scale factor
```

### AssetManager — Quick Reference

All asset keys are relative to `Asset/`. Extensions are auto-resolved.

```python
# Images
surf = game.AssetManager.image("Character/don_quixote")
surf = game.AssetManager.image_scaled("Character/don_quixote", (64, 64))

# Sound effects
game.AssetManager.play_sfx("Audio/hit", volume=0.8)

# Music (streaming, one track at a time)
game.AssetManager.play_music("Audio/theme", loops=-1, volume=0.5)
game.AssetManager.stop_music(fade_ms=500)

# Fonts
font = game.AssetManager.font("Fonts/pixel", size=24)
```

| Category | Supported Formats |
|---|---|
| Image | `.png` `.jpg` `.jpeg` `.bmp` `.gif` `.tga` `.webp` |
| SFX | `.wav` `.ogg` `.flac` |
| Music | `.mp3` `.ogg` `.mid` `.midi` `.mod` `.xm` |
| Font | `.ttf` `.otf` |

### EventManager

Register callbacks for any pygame event type:

```python
from Event import Event
game.eventManager.addEvent(Event(game, pygame.KEYDOWN, my_callback))
```

---

## Adding a New Entity

```python
# src/MyEntity.py
import pygame
from GameObject import GameObject

class MyEntity(GameObject):
    def __init__(self, game, x=0, y=0):
        super().__init__(game)
        self.x, self.y = x, y
        self.size = 50
        self.model = game.AssetManager.image_scaled("Character/don_quixote", (self.size, self.size))

    def update(self):
        pass  # per-frame logic

    def draw(self):
        self.drawModel()                                    # sprite
        self.drawRect((255, 255, 255), self.size, border_width=2)  # outline
```

Register it in `Game.__init__`:

```python
from MyEntity import MyEntity
entity = MyEntity(self, x=200, y=150)
self.objects.append(entity)
# If it should be selectable:
self.characters.append(entity)
```

---

## Documentation

Full per-class API reference, attribute tables, architecture diagrams, and notes:

→ [Documentation.md](Documentation.md)
