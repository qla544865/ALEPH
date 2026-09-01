import pygame


class GameObject:
    def __init__(self, game):
        self.x = 0
        self.y = 0

        self.game = game

        self.model: pygame.Surface = None

        self.size = 0

        self._cached_scale_key = None
        self._cached_scaled_model = None

        self.lods = []
        self.current_lod_key = None
        self.current_lod_sprite = None

    @property
    def screen_width(self):
        return self.game.surface.get_width()

    @property
    def screen_height(self):
        return self.game.surface.get_height()

    @property
    def screen_center_x(self):
        return self.screen_width // 2

    @property
    def screen_center_y(self):
        return self.screen_height // 2

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

    # ------------------------------------------------------------------
    # Visibility check (frustum culling)
    # ------------------------------------------------------------------

    def isOnScreen(self, screen_x, screen_y, width, height):
        """Return True if the rectangle overlaps the visible screen area."""
        sw = self.screen_width
        sh = self.screen_height
        return (
            screen_x + width > 0
            and screen_x < sw
            and screen_y + height > 0
            and screen_y < sh
        )

    def add_lod(self, scale_threshold: float,  sprite):
        self.lods.append((scale_threshold, sprite))
        self.lods.sort(key=lambda x: x[0], reverse=True)

        if self.current_lod_sprite is None:
            self.current_lod_sprite = sprite

    def update_lod(self):
        if not self.lods:
            return

        current_scale = self.getSizeScaleOnScreen()
        selected_sprite = self.lods[-1][1]

        for threshold, sprite in self.lods:
            if current_scale >= threshold:
                selected_sprite = sprite
                break

        if selected_sprite != self.current_lod_sprite:
            old_sprite = self.current_lod_sprite
            self.current_lod_sprite = selected_sprite
            
            if old_sprite and old_sprite.current_animation:
                anim_name = old_sprite.current_animation_name
                
                self.current_lod_sprite.play(anim_name) 
                
                if self.current_lod_sprite.current_animation:
                    self.current_lod_sprite.current_animation.current_frame_index = old_sprite.current_animation.current_frame_index
                    self.current_lod_sprite.current_animation.timer = old_sprite.current_animation.timer
            
            self._cached_scale_key = None

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def drawModel(self):
        if self.model is None:
            return

        scale = self.getSizeScaleOnScreen()
        screen_x, screen_y = self.getPositionOnScreen()

        scaled_width = int(self.model.get_width() * scale)
        scaled_height = int(self.model.get_height() * scale)

        if scaled_width <= 0 or scaled_height <= 0:
            return

        # --- frustum culling: skip if entirely off-screen ---
        if not self.isOnScreen(screen_x, screen_y, scaled_width, scaled_height):
            return

        # --- cached scale: only re-scale when source or target size change ---
        cache_key = (id(self.model), scaled_width, scaled_height)
        if self._cached_scale_key != cache_key:
            # Use smoothscale when zoomed in for higher detail,
            # regular scale when zoomed out for speed.
            if scale >= 1:
                self._cached_scaled_model = pygame.transform.smoothscale(
                    self.model, (scaled_width, scaled_height)
                )
            else:
                self._cached_scaled_model = pygame.transform.scale(
                    self.model, (scaled_width, scaled_height)
                )
            self._cached_scale_key = cache_key

        self.game.surface.blit(self._cached_scaled_model, (screen_x, screen_y))

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

