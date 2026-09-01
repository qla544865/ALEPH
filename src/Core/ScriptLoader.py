import pygame
import os
from lupa import LuaRuntime

ScriptDir = os.path.join(os.path.dirname(__file__), "..", "Script")


class ScriptLoader:
    def __init__(self, game):
        self.game = game
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.modules = {}

        self._bind_engine_apis()

    def _bind_engine_apis(self):
        # ------------------------------------------------------------------
        # 1. Logging & Print
        # ------------------------------------------------------------------
        def debug_log(*args):
            msg = " ".join(str(a) for a in args)
            print(f"[Debug/Lua]: {msg}")

        self.lua.globals().print = debug_log

        # ------------------------------------------------------------------
        # Key Mapping & Resolution
        # ------------------------------------------------------------------
        KEY_MAP = {
            "w": pygame.K_w, "a": pygame.K_a, "s": pygame.K_s, "d": pygame.K_d,
            "q": pygame.K_q, "e": pygame.K_e, "r": pygame.K_r, "f": pygame.K_f,
            "z": pygame.K_z, "x": pygame.K_x, "c": pygame.K_c, "v": pygame.K_v,
            "up": pygame.K_UP, "down": pygame.K_DOWN, "left": pygame.K_LEFT, "right": pygame.K_RIGHT,
            "space": pygame.K_SPACE, "escape": pygame.K_ESCAPE, "tab": pygame.K_TAB,
            "lshift": pygame.K_LSHIFT, "rshift": pygame.K_RSHIFT, "shift": pygame.K_LSHIFT,
            "lctrl": pygame.K_LCTRL, "rctrl": pygame.K_RCTRL, "ctrl": pygame.K_LCTRL,
            "lalt": pygame.K_LALT, "ralt": pygame.K_RALT, "alt": pygame.K_LALT,
            "return": pygame.K_RETURN, "enter": pygame.K_RETURN, "backspace": pygame.K_BACKSPACE,
            "minus": pygame.K_MINUS, "-": pygame.K_MINUS,
            "equals": pygame.K_EQUALS, "=": pygame.K_EQUALS, "plus": pygame.K_PLUS, "+": pygame.K_EQUALS,
            "home": pygame.K_HOME, "end": pygame.K_END,
            "pageup": pygame.K_PAGEUP, "pagedown": pygame.K_PAGEDOWN,
            "0": pygame.K_0, "1": pygame.K_1, "2": pygame.K_2, "3": pygame.K_3, "4": pygame.K_4,
            "5": pygame.K_5, "6": pygame.K_6, "7": pygame.K_7, "8": pygame.K_8, "9": pygame.K_9,
        }

        def _resolve_key(key):
            if isinstance(key, int):
                return key
            if isinstance(key, str):
                k = key.lower()
                if k in KEY_MAP:
                    return KEY_MAP[k]
                try:
                    return pygame.key.key_code(k)
                except (ValueError, pygame.error):
                    return None
            return None

        # ------------------------------------------------------------------
        # 2. Camera Namespace
        # ------------------------------------------------------------------
        def cam_get_pos():
            cam = getattr(self.game, 'camera', None)
            if cam:
                return float(cam.x), float(cam.y)
            return 0.0, 0.0

        def cam_set_pos(x, y):
            cam = getattr(self.game, 'camera', None)
            if cam:
                cam.x = float(x)
                cam.y = float(y)

        def cam_move(dx, dy):
            cam = getattr(self.game, 'camera', None)
            if cam:
                cam.x += float(dx)
                cam.y += float(dy)

        def cam_get_fov():
            cam = getattr(self.game, 'camera', None)
            return float(cam.fov) if cam else 0.0

        def cam_set_fov(fov):
            cam = getattr(self.game, 'camera', None)
            if cam:
                cam.fov = float(fov)
                cam.onChangeFov()

        def cam_change_fov(dfov):
            cam = getattr(self.game, 'camera', None)
            if cam:
                cam.fov += float(dfov)
                cam.onChangeFov()

        def cam_get_max_fov():
            cam = getattr(self.game, 'camera', None)
            return float(cam.mx_fov) if cam else 8.0

        def cam_get_scale():
            cam = getattr(self.game, 'camera', None)
            if cam:
                return float(max(0.1, 1.0 + (cam.fov * 0.1)))
            return 1.0

        def cam_get_world_mouse_pos():
            cam = getattr(self.game, 'camera', None)
            if cam:
                return cam.getWorldMousePos()
            return 0.0, 0.0

        def cam_screen_to_world(sx, sy):
            cam = getattr(self.game, 'camera', None)
            if not cam:
                return float(sx), float(sy)
            scale = max(0.1, 1.0 + (cam.fov * 0.1))
            cx = cam.screen_center_x
            cy = cam.screen_center_y
            wx = (float(sx) - cx) / scale + cam.x
            wy = (float(sy) - cy) / scale + cam.y
            return wx, wy

        def cam_world_to_screen(wx, wy):
            cam = getattr(self.game, 'camera', None)
            if not cam:
                return float(wx), float(wy)
            scale = max(0.1, 1.0 + (cam.fov * 0.1))
            cx = cam.screen_center_x
            cy = cam.screen_center_y
            sx = (float(wx) - cam.x) * scale + cx
            sy = (float(wy) - cam.y) * scale + cy
            return sx, sy

        def cam_reset():
            cam = getattr(self.game, 'camera', None)
            if cam:
                cam.x = 0.0
                cam.y = 0.0
                cam.fov = 0.0
                cam.onChangeFov()

        self.lua.globals().Camera = self.lua.table_from({
            'get_position': cam_get_pos,
            'get_pos': cam_get_pos,
            'set_position': cam_set_pos,
            'set_pos': cam_set_pos,
            'move': cam_move,
            'pan': cam_move,
            'get_fov': cam_get_fov,
            'set_fov': cam_set_fov,
            'change_fov': cam_change_fov,
            'zoom': cam_change_fov,
            'get_max_fov': cam_get_max_fov,
            'get_scale': cam_get_scale,
            'get_world_mouse_pos': cam_get_world_mouse_pos,
            'screen_to_world': cam_screen_to_world,
            'world_to_screen': cam_world_to_screen,
            'reset': cam_reset,
        })

        # ------------------------------------------------------------------
        # 3. Input Namespace
        # ------------------------------------------------------------------
        def input_is_key_pressed(key):
            code = _resolve_key(key)
            if code is None:
                return False
            key_pressed = getattr(self.game, 'keyPressed', None)
            if key_pressed is None:
                key_pressed = pygame.key.get_pressed()
            try:
                return bool(key_pressed[code])
            except Exception:
                return False

        def input_get_mouse_pos():
            mx, my = pygame.mouse.get_pos()
            return float(mx), float(my)

        def input_is_mouse_pressed(button=1):
            pressed = pygame.mouse.get_pressed()
            if isinstance(button, str):
                b = button.lower()
                if b in ("left", "l", "1"):
                    return bool(pressed[0])
                elif b in ("middle", "m", "2"):
                    return bool(pressed[1])
                elif b in ("right", "r", "3"):
                    return bool(pressed[2])
                return False
            if isinstance(button, (int, float)):
                idx = int(button) - 1  # 1-based indexing for Lua
                if 0 <= idx < len(pressed):
                    return bool(pressed[idx])
                if int(button) == 0:
                    return bool(pressed[0])
            return False

        def input_get_mouse_rel():
            dx, dy = pygame.mouse.get_rel()
            return float(dx), float(dy)

        def input_get_scroll():
            return getattr(self.game, 'scrolling', 0)

        def input_get_mouse_click_pos():
            pos = getattr(self.game, 'mouseClickPosition', (0, 0))
            return float(pos[0]), float(pos[1])

        def input_get_mouse_button_down():
            return getattr(self.game, 'mouseButtonDown', 0)

        self.lua.globals().Input = self.lua.table_from({
            'is_key_pressed': input_is_key_pressed,
            'is_key_down': input_is_key_pressed,
            'get_mouse_pos': input_get_mouse_pos,
            'is_mouse_pressed': input_is_mouse_pressed,
            'is_mouse_down': input_is_mouse_pressed,
            'get_mouse_rel': input_get_mouse_rel,
            'get_scroll': input_get_scroll,
            'get_mouse_wheel': input_get_scroll,
            'get_mouse_click_pos': input_get_mouse_click_pos,
            'get_mouse_button_down': input_get_mouse_button_down,
        })

        # ------------------------------------------------------------------
        # 4. Engine & Time Namespaces
        # ------------------------------------------------------------------
        def engine_get_dt():
            return float(getattr(self.game, 'dt', 0.0))

        def engine_get_fps():
            clock = getattr(self.game, 'clock', None)
            return float(clock.get_fps()) if clock else 0.0

        def engine_get_screen_size():
            surface = getattr(self.game, 'surface', None)
            if surface:
                return float(surface.get_width()), float(surface.get_height())
            return 1280.0, 720.0

        def engine_get_screen_center():
            w, h = engine_get_screen_size()
            return w // 2, h // 2

        self.lua.globals().Engine = self.lua.table_from({
            'get_dt': engine_get_dt,
            'get_fps': engine_get_fps,
            'get_screen_size': engine_get_screen_size,
            'get_screen_center': engine_get_screen_center,
            'log': debug_log,
        })

        self.lua.globals().Time = self.lua.table_from({
            'get_dt': engine_get_dt,
            'get_fps': engine_get_fps,
        })

        # ------------------------------------------------------------------
        # 5. Key Constants Table
        # ------------------------------------------------------------------
        self.lua.globals().Key = self.lua.table_from({
            'W': 'w', 'A': 'a', 'S': 's', 'D': 'd',
            'Q': 'q', 'E': 'e', 'R': 'r', 'F': 'f',
            'Z': 'z', 'X': 'x', 'C': 'c', 'V': 'v',
            'UP': 'up', 'DOWN': 'down', 'LEFT': 'left', 'RIGHT': 'right',
            'SPACE': 'space', 'ESCAPE': 'escape', 'TAB': 'tab',
            'SHIFT': 'shift', 'CTRL': 'ctrl', 'ALT': 'alt',
            'LSHIFT': 'lshift', 'RSHIFT': 'rshift',
            'LCTRL': 'lctrl', 'RCTRL': 'rctrl',
            'MINUS': '-', 'EQUALS': '=', 'PLUS': '+',
            'HOME': 'home', 'END': 'end',
            'PAGEUP': 'pageup', 'PAGEDOWN': 'pagedown',
            'RETURN': 'return', 'ENTER': 'return', 'BACKSPACE': 'backspace',
        })

    def load_all(self):
        if not os.path.exists(ScriptDir):
            os.makedirs(ScriptDir, exist_ok=True)
        for filename in os.listdir(ScriptDir):
            if filename.endswith(".lua"):
                self.load_script(filename)

    def load_script(self, filename):
        filepath = os.path.join(ScriptDir, filename)
        module_name = filename.replace(".lua", "")
        
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                code = file.read()

            lua_module = self.lua.execute(code)
            self.modules[module_name] = lua_module

            if lua_module is not None:
                init_fn = getattr(lua_module, 'init', None)
                if init_fn:
                    init_fn()
                
            print(f"[Loader] Loaded module: {module_name}")
        except Exception as e:
            print(f"[Loader] Failed to load {filename}: {e}")

    def update(self, delta_time):
        for name, module in self.modules.items():
            if module is not None:
                try:
                    update_fn = getattr(module, 'update', None)
                    if update_fn:
                        update_fn(delta_time)
                except Exception as e:
                    print(f"[Script Error] Error updating {name}: {e}")