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
│   ├── GameObject.py       # Base class for world entities
│   ├── Camera.py           # Pan & zoom camera
│   ├── Selection.py        # Marquee (rubber-band) selection
│   ├── Event.py            # Event dispatcher
│   ├── AssetManager.py     # Lazy-loading asset cache
│   ├── Character.py        # Character entity
│   └── testObj.py          # Debug grid object
└── requirements.txt
```

---

## Architecture

```
main.py  →  Game
              ├── Camera          (extends GameObject)
              ├── MarqueeSelection(extends GameObject)
              ├── EventManager    (dispatches Event callbacks)
              ├── AssetManager    (images, SFX, music, fonts)
              └── objects[]       (TestObj, Character, ...)
```

**Frame loop** — every tick:

```
eventHandle()  →  update()  →  draw()
```

See [ALEPH_Documentation.md](ALEPH_Documentation.md) for the full per-class API reference.

---

## Controls

| Input | Action |
|---|---|
| `W / A / S / D` | Pan camera |
| `+` / `-` | Zoom in / out |
| Mouse wheel | Zoom in / out |
| Right-click drag | Pan camera |
| Left-click drag | Marquee select |

---

## AssetManager — Quick Reference

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

    def update(self):
        pass  # per-frame logic

    def draw(self):
        cam   = self.game.camera
        scale = max(0.1, 1.0 + cam.fov * 0.1)
        cx, cy = self.game.surface.get_width() // 2, self.game.surface.get_height() // 2
        sx = (self.x - cam.x) * scale + cx
        sy = (self.y - cam.y) * scale + cy
        pygame.draw.circle(self.game.surface, (255, 0, 0), (int(sx), int(sy)), 20)
```

Register it in `Game.__init__`:

```python
from MyEntity import MyEntity
self.objects.append(MyEntity(self, x=200, y=150))
```

---

## Documentation

Full per-class API reference, attribute tables, architecture diagrams, and notes:

→ [Documentation.md](Documentation.md)
