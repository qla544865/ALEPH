# ALEPH

A 2D game framework built on **pygame** with a **Lua scripting system**, zoomable/pannable camera, sprite animation, LOD system, marquee selection, and a centralised asset manager.

> **Python 3.10.1** · **pygame 2.6.1** · **lupa ≥ 2.0**

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
│   ├── Character/          # Character sprites
│   └── Items/              # Item sprites
├── src/
│   ├── main.py             # Entry point
│   ├── Core/               # Python engine modules
│   │   ├── Game.py         # Game loop, loading screen, subsystem wiring
│   │   ├── GameObject.py   # Base class — position, LOD, drawing helpers
│   │   ├── Camera.py       # Camera (script-controlled)
│   │   ├── Selection.py    # Marquee (rubber-band) selection
│   │   ├── Event.py        # Event dispatcher
│   │   ├── AssetManager.py # Lazy-loading asset cache + sprite helpers
│   │   ├── ScriptLoader.py # Lua runtime, API bindings, script hot-loading
│   │   ├── Sprite.py       # SpriteSheet, Animation, Sprite classes
│   │   ├── Character.py    # Character entity
│   │   ├── Item.py         # GameItem entity
│   │   └── testObj.py      # TestObj (debug grid) & TestMouse (cursor dot)
│   └── Script/             # Lua scripts (auto-loaded at startup)
│       ├── CameraController.lua
│       └── TestSystem.lua
├── .gitignore
└── requirements.txt
```

---

## Architecture

```
main.py  →  Game
              ├── AssetManager      (images, sprites, SFX, music, fonts)
              ├── ScriptLoader      (Lua runtime + Camera/Input/Engine APIs)
              ├── Camera            (extends GameObject, script-controlled)
              ├── MarqueeSelection  (extends GameObject)
              ├── EventManager      (dispatches Event callbacks)
              ├── objects[]         (TestObj, Character, GameItem, TestMouse)
              └── characters[]      (selectable entities)
```

**Frame loop** — every tick:

```
eventHandle()  →  update()  →  draw()
     │               │
     │        ScriptLoader.update(dt)   ← runs Lua update() each frame
     └── VIDEORESIZE handled → resizable window
```

See [Documentation.md](Documentation.md) for the full API reference.

---

## Controls

> Camera is now **fully script-controlled** via `CameraController.lua`.

| Input | Action |
|---|---|
| `W / A / S / D` or Arrow keys | Pan camera |
| `Shift` + pan keys | Fast pan (2.5×) |
| `+` / `-` | Zoom in / out |
| Mouse wheel | Zoom (faster) |
| Right-click drag | Pan camera |
| `R` | Reset camera |
| Left-click drag | Marquee select |
| Left-click (no drag) | Toggle select single character |

---

## Lua Scripting

Drop any `.lua` file into `src/Script/`. It is loaded automatically at startup.

### Module Convention

```lua
local MySystem = {}

function MySystem.init()
    -- Called once on load
end

function MySystem.update(dt)
    -- Called every frame, dt = delta time in seconds
end

return MySystem
```

### Built-in Global APIs

| Global | Description |
|---|---|
| `Camera` | Pan, zoom, reset, coordinate conversion |
| `Input` | Key/mouse state queries |
| `Engine` | DT, FPS, screen size |
| `Time` | Alias for Engine (DT, FPS) |
| `Key` | Named key constants (e.g. `Key.W`, `Key.SPACE`) |

#### Camera API

```lua
Camera.get_pos()               -- returns x, y
Camera.set_pos(x, y)
Camera.move(dx, dy)            -- alias: Camera.pan
Camera.get_fov()
Camera.set_fov(fov)
Camera.change_fov(dfov)        -- alias: Camera.zoom
Camera.get_scale()             -- current zoom scale factor
Camera.get_world_mouse_pos()   -- mouse position in world coords
Camera.screen_to_world(sx, sy)
Camera.world_to_screen(wx, wy)
Camera.reset()                 -- x=0, y=0, fov=0
```

#### Input API

```lua
Input.is_key_pressed("w")           -- also: Key.W, "up", "space", etc.
Input.get_mouse_pos()               -- returns mx, my (screen)
Input.is_mouse_pressed(1)           -- 1=left, 2=middle, 3=right  or "left"/"right"
Input.get_scroll()                  -- mouse wheel delta
Input.get_mouse_rel()               -- dx, dy since last frame
```

#### Engine / Time API

```lua
Engine.get_dt()           -- delta time in seconds
Engine.get_fps()
Engine.get_screen_size()  -- returns w, h
Engine.log("message")     -- prints to console with [Debug/Lua] prefix
```

---

## Adding a New Entity

```python
# src/Core/MyEntity.py
from Core.GameObject import GameObject

class MyEntity(GameObject):
    def __init__(self, game, x=0, y=0):
        super().__init__(game)
        self.x, self.y = x, y
        self.size = (64, 64)
        self.model = game.AssetManager.image_scaled("Character/don_quixote", self.size)

    def update(self): pass

    def draw(self):
        sx, sy = self.getPositionOnScreen()
        scale = self.getSizeScaleOnScreen()
        sw = int(self.size[0] * scale)
        sh = int(self.size[1] * scale)
        if self.isOnScreen(sx, sy, sw, sh):
            self.drawModel()
            self.drawRect((255, 255, 255), self.size, border_width=2)
```

Register in `Game._load_character()`:

```python
entity = MyEntity(self, x=200, y=150)
self.objects.append(entity)
self.characters.append(entity)  # if selectable
```

---

## Adding a New Lua Script

Create `src/Script/MyScript.lua`:

```lua
local MyScript = {}

function MyScript.init()
    Engine.log("MyScript loaded!")
end

function MyScript.update(dt)
    if Input.is_key_pressed(Key.SPACE) then
        Camera.reset()
    end
end

return MyScript
```

It will be discovered and loaded automatically next run.

---

## Documentation

Full per-class API reference, architecture diagrams, and guides:

→ [Documentation.md](Documentation.md)
