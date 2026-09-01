import pygame
import os


# Root asset folder relative to this file's location
ASSET_DIR = os.path.join(os.path.dirname(__file__), "..\..", "Asset")

# Supported file extensions per category
IMAGE_EXTS  = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tga", ".webp"}
SFX_EXTS    = {".wav", ".ogg", ".flac"}
MUSIC_EXTS  = {".mp3", ".ogg", ".mid", ".midi", ".mod", ".xm"}
FONT_EXTS   = {".ttf", ".otf"}


class AssetManager:
    """Central asset manager for a pygame project.

    Handles lazy-loading and caching of:
      - Images   (pygame.Surface)
      - SFX      (pygame.mixer.Sound)
      - Music    (streamed via pygame.mixer.music)
      - Fonts    (pygame.font.Font)

    All paths are resolved relative to the ``Asset/`` folder at the
    project root, so callers only need short keys like
    ``"Character/don_quixote"`` or ``"Audio/jump"``.

    Usage
    -----
    assets = AssetManager(game)

    # Images
    surf = assets.image("Character/don_quixote")

    # SFX  (plays instantly, cached)
    assets.sfx("Audio/hit").play()

    # Music  (streamed; only one track at a time)
    assets.play_music("Audio/theme", loops=-1, volume=0.5)
    assets.stop_music()

    # Fonts
    font = assets.font("Fonts/pixel", size=24)
    """

    def __init__(self, game):
        self.game = game
        pygame.mixer.init()

        # Caches  {key: asset}
        self._images: dict[str, pygame.Surface] = {}
        self._sfx:    dict[str, pygame.mixer.Sound] = {}
        self._fonts:  dict[tuple, pygame.font.Font] = {}  # (key, size) -> Font

        self._music_volume: float = 1.0
        self._current_music: str | None = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve(self, key: str, extensions: set[str]) -> str:
        """Return the first matching file path for *key* + any of *extensions*.

        If *key* already has a supported extension it is used as-is.
        Raises ``FileNotFoundError`` if nothing is found.
        """
        base = os.path.join(ASSET_DIR, key)

        # Already has an extension
        if os.path.splitext(key)[1].lower() in extensions:
            if os.path.isfile(base):
                return base

        # Try appending each supported extension
        for ext in extensions:
            candidate = base + ext
            if os.path.isfile(candidate):
                return candidate

        raise FileNotFoundError(
            f"Asset not found: '{key}'  (searched in '{ASSET_DIR}' "
            f"with extensions {extensions})"
        )

    # ------------------------------------------------------------------
    # Images
    # ------------------------------------------------------------------

    def image(self, key: str, alpha: bool = True) -> pygame.Surface:
        """Return a cached ``pygame.Surface`` for *key*.

        Parameters
        ----------
        key:
            Path relative to ``Asset/``, with or without extension.
        alpha:
            If ``True`` (default) calls ``convert_alpha()``, otherwise
            ``convert()`` for opaque images (slightly faster blitting).
        """
        if key not in self._images:
            path = self._resolve(key, IMAGE_EXTS)
            surf = pygame.image.load(path)
            self._images[key] = surf.convert_alpha() if alpha else surf.convert()
        return self._images[key]

    def image_scaled(
        self, key: str, size: tuple[int, int], alpha: bool = True
    ) -> pygame.Surface:
        """Return a *new* scaled copy of the image (not cached by size)."""
        return pygame.transform.scale(self.image(key, alpha), size)

    def unload_image(self, key: str) -> None:
        """Remove a cached image to free memory."""
        self._images.pop(key, None)

    # ------------------------------------------------------------------
    # Sprites & Animations
    # ------------------------------------------------------------------

    def spritesheet(self, key: str, alpha: bool = True):
        """Return a ``SpriteSheet`` for *key*."""
        from Core.Sprite import SpriteSheet
        return SpriteSheet.from_asset(self, key, alpha=alpha)

    def animation(
        self,
        key: str,
        cols: int,
        rows: int,
        fps: float = 12.0,
        loop: bool = True,
        frame_count: int | None = None,
        scale_size: tuple[int, int] | None = None,
        alpha: bool = True,
    ):
        """Load a sprite sheet and return an ``Animation`` from a grid."""
        from Core.Sprite import load_animation
        return load_animation(
            self,
            key=key,
            cols=cols,
            rows=rows,
            fps=fps,
            loop=loop,
            frame_count=frame_count,
            scale_size=scale_size,
            alpha=alpha,
        )

    def animated_sprite(
        self,
        key: str,
        cols: int = 1,
        rows: int = 1,
        fps: float = 12.0,
        loop: bool = True,
        frame_count: int | None = None,
        scale_size: tuple[int, int] | None = None,
        animation_name: str = "default",
        alpha: bool = True,
    ):
        """Load a sprite sheet grid and return a ready-to-use ``Sprite``."""
        from Core.Sprite import load_sprite
        return load_sprite(
            self,
            key=key,
            cols=cols,
            rows=rows,
            fps=fps,
            loop=loop,
            frame_count=frame_count,
            scale_size=scale_size,
            animation_name=animation_name,
            alpha=alpha,
        )

    # ------------------------------------------------------------------
    # SFX
    # ------------------------------------------------------------------

    def sfx(self, key: str) -> pygame.mixer.Sound:
        """Return a cached ``pygame.mixer.Sound`` for *key*.

        Call ``.play()`` on the result to trigger the sound.
        """
        if key not in self._sfx:
            path = self._resolve(key, SFX_EXTS)
            self._sfx[key] = pygame.mixer.Sound(path)
        return self._sfx[key]

    def play_sfx(self, key: str, volume: float = 1.0, loops: int = 0) -> None:
        """Convenience: load, set volume, and play a sound effect."""
        sound = self.sfx(key)
        sound.set_volume(volume)
        sound.play(loops=loops)

    def stop_sfx(self, key: str) -> None:
        """Stop a specific sound effect if it is playing."""
        if key in self._sfx:
            self._sfx[key].stop()

    def unload_sfx(self, key: str) -> None:
        """Remove a cached sound from memory."""
        self._sfx.pop(key, None)

    # ------------------------------------------------------------------
    # Music  (streamed – only one track plays at a time)
    # ------------------------------------------------------------------

    def play_music(
        self,
        key: str,
        loops: int = -1,
        volume: float | None = None,
        start: float = 0.0,
        fade_ms: int = 0,
    ) -> None:
        """Stream music from *key*.

        Parameters
        ----------
        key:
            Path relative to ``Asset/``, with or without extension.
        loops:
            Number of extra repeats; ``-1`` loops forever.
        volume:
            0.0 – 1.0.  If ``None``, keeps the current volume.
        start:
            Start position in seconds.
        fade_ms:
            Fade-in duration in milliseconds.
        """
        path = self._resolve(key, MUSIC_EXTS)
        if volume is not None:
            self._music_volume = volume
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(self._music_volume)
        pygame.mixer.music.play(loops=loops, start=start, fade_ms=fade_ms)
        self._current_music = key

    def stop_music(self, fade_ms: int = 0) -> None:
        """Stop the currently playing music.

        Parameters
        ----------
        fade_ms:
            If > 0, fades out over that many milliseconds.
        """
        if fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()
        self._current_music = None

    def pause_music(self) -> None:
        pygame.mixer.music.pause()

    def resume_music(self) -> None:
        pygame.mixer.music.unpause()

    def set_music_volume(self, volume: float) -> None:
        """Set music volume (0.0 – 1.0)."""
        self._music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self._music_volume)

    @property
    def current_music(self) -> str | None:
        """Key of the currently loaded music track, or ``None``."""
        return self._current_music

    # ------------------------------------------------------------------
    # Fonts
    # ------------------------------------------------------------------

    def font(self, key: str, size: int = 16) -> pygame.font.Font:
        """Return a cached ``pygame.font.Font`` for (*key*, *size*).

        Pass ``key=""`` or ``key=None`` to use pygame's built-in default font.
        """
        cache_key = (key, size)
        if cache_key not in self._fonts:
            if key:
                path = self._resolve(key, FONT_EXTS)
                self._fonts[cache_key] = pygame.font.Font(path, size)
            else:
                self._fonts[cache_key] = pygame.font.Font(None, size)
        return self._fonts[cache_key]

    def sysfont(self, name: str, size: int = 16) -> pygame.font.Font:
        """Return a cached ``pygame.font.SysFont``."""
        cache_key = (f"__sys__{name}", size)
        if cache_key not in self._fonts:
            self._fonts[cache_key] = pygame.font.SysFont(name, size)
        return self._fonts[cache_key]

    # ------------------------------------------------------------------
    # Bulk operations
    # ------------------------------------------------------------------

    def preload_images(self, *keys: str, alpha: bool = True) -> None:
        """Load multiple images at once (e.g. during a loading screen)."""
        for key in keys:
            self.image(key, alpha)

    def preload_sfx(self, *keys: str) -> None:
        """Load multiple sound effects at once."""
        for key in keys:
            self.sfx(key)

    def clear_images(self) -> None:
        """Evict all cached images."""
        self._images.clear()

    def clear_sfx(self) -> None:
        """Evict all cached sound effects."""
        self._sfx.clear()

    def clear_fonts(self) -> None:
        """Evict all cached fonts."""
        self._fonts.clear()

    def clear_all(self) -> None:
        """Evict everything from all caches."""
        self.clear_images()
        self.clear_sfx()
        self.clear_fonts()

    # ------------------------------------------------------------------
    # Debug
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"<AssetManager "
            f"images={len(self._images)} "
            f"sfx={len(self._sfx)} "
            f"fonts={len(self._fonts)} "
            f"music={self._current_music!r}>"
        )
