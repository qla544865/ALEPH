import pygame
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from Core.AssetManager import AssetManager


class SpriteSheet:
    """Represents a sprite sheet image and provides frame extraction utilities.

    Can be instantiated from an existing ``pygame.Surface`` or loaded
    directly via ``AssetManager``:

    Usage
    -----
    # Via AssetManager helper
    sheet = SpriteSheet.from_asset(game.AssetManager, "Character/la_manchaland_sprite")

    # Or from a surface
    sheet = SpriteSheet(surface)

    # Extract all frames from a 10x6 grid
    frames = sheet.get_frames_grid(cols=10, rows=6)
    """

    def __init__(self, surface: pygame.Surface):
        self.surface = surface
        self.width = surface.get_width()
        self.height = surface.get_height()

    @classmethod
    def from_asset(
        cls,
        asset_manager: "AssetManager",
        key: str,
        alpha: bool = True,
    ) -> "SpriteSheet":
        """Load a sprite sheet using an ``AssetManager`` instance."""
        surface = asset_manager.image(key, alpha=alpha)
        return cls(surface)

    def get_frame(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        scale_size: tuple[int, int] | None = None,
    ) -> pygame.Surface:
        """Extract a single rectangular frame from the sprite sheet.

        Parameters
        ----------
        x, y:
            Top-left pixel coordinates of the frame.
        width, height:
            Dimensions of the frame in pixels.
        scale_size:
            Optional ``(width, height)`` to scale the extracted frame.
        """
        rect = pygame.Rect(x, y, width, height)
        frame = pygame.Surface((width, height), pygame.SRCALPHA)
        frame.blit(self.surface, (0, 0), rect)

        if scale_size is not None:
            frame = pygame.transform.scale(frame, scale_size)

        return frame

    def get_frame_by_index(
        self,
        col: int,
        row: int,
        frame_width: int,
        frame_height: int,
        scale_size: tuple[int, int] | None = None,
        margin: int = 0,
        spacing: int = 0,
    ) -> pygame.Surface:
        """Extract a frame by grid coordinates ``(col, row)``."""
        x = margin + col * (frame_width + spacing)
        y = margin + row * (frame_height + spacing)
        return self.get_frame(x, y, frame_width, frame_height, scale_size)

    def get_frames_grid(
        self,
        cols: int,
        rows: int,
        frame_count: int | None = None,
        scale_size: tuple[int, int] | None = None,
        margin: int = 0,
        spacing: int = 0,
    ) -> list[pygame.Surface]:
        """Extract all frames from a uniform grid (left-to-right, top-to-bottom).

        Parameters
        ----------
        cols:
            Number of columns in the grid.
        rows:
            Number of rows in the grid.
        frame_count:
            Total frames to extract. Defaults to ``cols * rows``.
        scale_size:
            Optional ``(width, height)`` to scale each frame to.
        margin:
            Outer border margin in pixels.
        spacing:
            Gap between adjacent frames in pixels.
        """
        available_w = self.width - 2 * margin - (cols - 1) * spacing
        available_h = self.height - 2 * margin - (rows - 1) * spacing
        frame_width = available_w // cols
        frame_height = available_h // rows

        total = frame_count if frame_count is not None else (cols * rows)
        frames: list[pygame.Surface] = []

        for row in range(rows):
            for col in range(cols):
                if len(frames) >= total:
                    break
                frame = self.get_frame_by_index(
                    col=col,
                    row=row,
                    frame_width=frame_width,
                    frame_height=frame_height,
                    scale_size=scale_size,
                    margin=margin,
                    spacing=spacing,
                )
                frames.append(frame)
            if len(frames) >= total:
                break

        return frames

    def get_row_frames(
        self,
        row: int,
        cols: int,
        rows: int,
        frame_count: int | None = None,
        scale_size: tuple[int, int] | None = None,
        margin: int = 0,
        spacing: int = 0,
    ) -> list[pygame.Surface]:
        """Extract frames from a specific row in a uniform grid."""
        available_w = self.width - 2 * margin - (cols - 1) * spacing
        available_h = self.height - 2 * margin - (rows - 1) * spacing
        frame_width = available_w // cols
        frame_height = available_h // rows

        total = frame_count if frame_count is not None else cols
        frames: list[pygame.Surface] = []

        for col in range(cols):
            if len(frames) >= total:
                break
            frame = self.get_frame_by_index(
                col=col,
                row=row,
                frame_width=frame_width,
                frame_height=frame_height,
                scale_size=scale_size,
                margin=margin,
                spacing=spacing,
            )
            frames.append(frame)

        return frames

    def get_col_frames(
        self,
        col: int,
        cols: int,
        rows: int,
        frame_count: int | None = None,
        scale_size: tuple[int, int] | None = None,
        margin: int = 0,
        spacing: int = 0,
    ) -> list[pygame.Surface]:
        """Extract frames from a specific column in a uniform grid."""
        available_w = self.width - 2 * margin - (cols - 1) * spacing
        available_h = self.height - 2 * margin - (rows - 1) * spacing
        frame_width = available_w // cols
        frame_height = available_h // rows

        total = frame_count if frame_count is not None else rows
        frames: list[pygame.Surface] = []

        for row in range(rows):
            if len(frames) >= total:
                break
            frame = self.get_frame_by_index(
                col=col,
                row=row,
                frame_width=frame_width,
                frame_height=frame_height,
                scale_size=scale_size,
                margin=margin,
                spacing=spacing,
            )
            frames.append(frame)

        return frames


class Animation:
    """Manages frame playback, timing, looping, and scaling of an animation sequence.

    Parameters
    ----------
    frames:
        List of ``pygame.Surface`` frames in playback order.
    fps:
        Playback rate in frames per second (default: 12.0).
    loop:
        If ``True`` (default), restarts from frame 0 upon reaching the end.
    playback_speed:
        Multiplier for playback speed (1.0 = normal).
    on_finish:
        Optional callback triggered when a non-looping animation finishes.
    """

    def __init__(
        self,
        frames: list[pygame.Surface],
        fps: float = 12.0,
        loop: bool = True,
        playback_speed: float = 1.0,
        on_finish: Callable[[], None] | None = None,
    ):
        if not frames:
            raise ValueError("Animation must contain at least one frame.")

        self.frames: list[pygame.Surface] = list(frames)
        self.fps: float = fps
        self.loop: bool = loop
        self.playback_speed: float = playback_speed
        self.on_finish: Callable[[], None] | None = on_finish

        self.current_frame_index: int = 0
        self.timer: float = 0.0
        self.is_playing: bool = True
        self.is_finished: bool = False

    @property
    def frame_duration(self) -> float:
        """Duration of a single frame in seconds."""
        if self.fps <= 0:
            return float("inf")
        return (1.0 / self.fps) / max(0.0001, self.playback_speed)

    @property
    def total_duration(self) -> float:
        """Total duration of one complete animation cycle in seconds."""
        return len(self.frames) * self.frame_duration

    @property
    def current_frame(self) -> pygame.Surface:
        """Return the currently active ``pygame.Surface`` frame."""
        return self.frames[self.current_frame_index]

    def update(self, dt: float) -> pygame.Surface:
        """Advance the animation by *dt* seconds and return the current frame.

        Parameters
        ----------
        dt:
            Delta time in seconds (e.g. from ``game.dt``).
        """
        if not self.is_playing or len(self.frames) <= 1:
            return self.current_frame

        duration = self.frame_duration
        if duration <= 0:
            return self.current_frame

        self.timer += dt
        while self.timer >= duration:
            self.timer -= duration
            if self.current_frame_index + 1 < len(self.frames):
                self.current_frame_index += 1
            else:
                if self.loop:
                    self.current_frame_index = 0
                else:
                    self.current_frame_index = len(self.frames) - 1
                    self.is_playing = False
                    self.is_finished = True
                    if self.on_finish is not None:
                        self.on_finish()
                    break

        return self.current_frame

    def play(self) -> None:
        """Resume playback or restart if already finished."""
        if self.is_finished:
            self.restart()
        else:
            self.is_playing = True

    def pause(self) -> None:
        """Pause playback at current frame."""
        self.is_playing = False

    def stop(self) -> None:
        """Stop playback and rewind to the first frame."""
        self.is_playing = False
        self.current_frame_index = 0
        self.timer = 0.0
        self.is_finished = False

    def restart(self) -> None:
        """Rewind to the first frame and start playback."""
        self.current_frame_index = 0
        self.timer = 0.0
        self.is_playing = True
        self.is_finished = False

    def set_frame(self, index: int) -> None:
        """Jump directly to a frame index."""
        self.current_frame_index = max(0, min(len(self.frames) - 1, index))
        self.timer = 0.0

    def scaled(self, size: tuple[int, int]) -> "Animation":
        """Return a new ``Animation`` with all frames scaled to (*width*, *height*)."""
        scaled_frames = [pygame.transform.scale(f, size) for f in self.frames]
        return Animation(
            scaled_frames,
            fps=self.fps,
            loop=self.loop,
            playback_speed=self.playback_speed,
            on_finish=self.on_finish,
        )

    def flipped(self, flip_x: bool = False, flip_y: bool = False) -> "Animation":
        """Return a new ``Animation`` with all frames flipped horizontally/vertically."""
        flipped_frames = [
            pygame.transform.flip(f, flip_x, flip_y) for f in self.frames
        ]
        return Animation(
            flipped_frames,
            fps=self.fps,
            loop=self.loop,
            playback_speed=self.playback_speed,
            on_finish=self.on_finish,
        )

    def copy(self) -> "Animation":
        """Return an independent copy sharing the same frame surfaces."""
        return Animation(
            self.frames,
            fps=self.fps,
            loop=self.loop,
            playback_speed=self.playback_speed,
            on_finish=self.on_finish,
        )

    def __len__(self) -> int:
        return len(self.frames)

    def __repr__(self) -> str:
        return (
            f"<Animation frames={len(self.frames)} "
            f"fps={self.fps} "
            f"loop={self.loop} "
            f"playing={self.is_playing} "
            f"frame={self.current_frame_index}>"
        )


class Sprite:
    """High-level sprite controller supporting static images and named animations.

    Can be plugged into a ``GameObject`` entity or used independently.

    Usage
    -----
    # From an AssetManager sprite sheet:
    sprite = Sprite.from_grid(
        game.AssetManager,
        "Character/la_manchaland_sprite",
        cols=10,
        rows=6,
        fps=24.0
    )

    # In entity update:
    sprite.update(game.dt)

    # In entity draw or model assignment:
    self.model = sprite.current_frame
    """

    def __init__(
        self,
        default_image: pygame.Surface | None = None,
        animations: dict[str, Animation] | None = None,
        default_animation: str | None = None,
    ):
        self._animations: dict[str, Animation] = dict(animations) if animations else {}
        self._default_image: pygame.Surface | None = default_image
        self._current_animation_name: str | None = None
        self.flip_x: bool = False
        self.flip_y: bool = False

        if default_animation and default_animation in self._animations:
            self.play(default_animation)
        elif self._animations:
            first_name = next(iter(self._animations))
            self.play(first_name)

    @property
    def current_animation(self) -> Animation | None:
        """Currently active ``Animation`` instance, or ``None``."""
        if self._current_animation_name is not None:
            return self._animations.get(self._current_animation_name)
        return None

    @property
    def current_animation_name(self) -> str | None:
        """Name of the currently active animation."""
        return self._current_animation_name

    @property
    def current_frame(self) -> pygame.Surface | None:
        """Return the current frame surface (with flip applied if set)."""
        surf: pygame.Surface | None = None
        if self.current_animation is not None:
            surf = self.current_animation.current_frame
        elif self._default_image is not None:
            surf = self._default_image

        if surf is not None and (self.flip_x or self.flip_y):
            return pygame.transform.flip(surf, self.flip_x, self.flip_y)
        return surf

    @property
    def model(self) -> pygame.Surface | None:
        """Alias for ``current_frame``, matching ``GameObject.model`` naming."""
        return self.current_frame

    @property
    def is_playing(self) -> bool:
        """Whether the active animation is currently playing."""
        if self.current_animation is not None:
            return self.current_animation.is_playing
        return False

    @property
    def is_finished(self) -> bool:
        """Whether the active animation has finished playing (for non-looping)."""
        if self.current_animation is not None:
            return self.current_animation.is_finished
        return True

    def add_animation(self, name: str, animation: Animation) -> None:
        """Add a named animation to the sprite."""
        self._animations[name] = animation
        if self._current_animation_name is None:
            self.play(name)

    def play(self, name: str | None = None, restart: bool = False) -> None:
        """Play an animation by name, or resume the current animation if name is None."""
        if name is not None:
            if name not in self._animations:
                raise KeyError(
                    f"Animation '{name}' not found in Sprite. Available: {list(self._animations.keys())}"
                )
            if self._current_animation_name != name:
                self._current_animation_name = name
                self._animations[name].restart()
            elif restart:
                self._animations[name].restart()
            else:
                self._animations[name].play()
        elif self.current_animation is not None:
            if restart:
                self.current_animation.restart()
            else:
                self.current_animation.play()

    def pause(self) -> None:
        """Pause the current animation."""
        if self.current_animation is not None:
            self.current_animation.pause()

    def stop(self) -> None:
        """Stop and rewind the current animation."""
        if self.current_animation is not None:
            self.current_animation.stop()

    def restart(self) -> None:
        """Rewind and play the current animation."""
        if self.current_animation is not None:
            self.current_animation.restart()

    def set_frame(self, index: int) -> None:
        """Set the frame index of the current animation."""
        if self.current_animation is not None:
            self.current_animation.set_frame(index)

    def update(self, dt: float) -> pygame.Surface | None:
        """Update the active animation by *dt* seconds and return the current frame."""
        if self.current_animation is not None:
            self.current_animation.update(dt)
        return self.current_frame

    def draw(self, surface: pygame.Surface, dest: tuple[int, int] | pygame.Rect) -> None:
        """Draw the current frame to *surface* at *dest*."""
        frame = self.current_frame
        if frame is not None:
            surface.blit(frame, dest)

    @classmethod
    def from_grid(
        cls,
        asset_manager_or_sheet: "AssetManager | SpriteSheet | pygame.Surface",
        key: str | None = None,
        cols: int = 1,
        rows: int = 1,
        fps: float = 12.0,
        loop: bool = True,
        frame_count: int | None = None,
        scale_size: tuple[int, int] | None = None,
        animation_name: str = "default",
        alpha: bool = True,
    ) -> "Sprite":
        """Create a ``Sprite`` with a default animation loaded from a grid.

        Parameters
        ----------
        asset_manager_or_sheet:
            An ``AssetManager`` instance, a ``SpriteSheet``, or a ``pygame.Surface``.
        key:
            Asset key relative to ``Asset/`` (required if first argument is ``AssetManager``).
        cols:
            Number of columns in the sprite sheet.
        rows:
            Number of rows in the sprite sheet.
        fps:
            Animation frame rate in frames per second.
        loop:
            Whether the animation loops.
        frame_count:
            Total frames to extract (defaults to ``cols * rows``).
        scale_size:
            Optional ``(width, height)`` to scale each frame to.
        animation_name:
            Name for the initial animation (default: ``"default"``).
        alpha:
            Whether to load with alpha channel (when passing AssetManager).
        """
        if hasattr(asset_manager_or_sheet, "image"):
            if key is None:
                raise ValueError("An asset key must be provided when using AssetManager.")
            sheet = SpriteSheet.from_asset(asset_manager_or_sheet, key, alpha=alpha)
        elif isinstance(asset_manager_or_sheet, SpriteSheet):
            sheet = asset_manager_or_sheet
        elif isinstance(asset_manager_or_sheet, pygame.Surface):
            sheet = SpriteSheet(asset_manager_or_sheet)
        else:
            raise TypeError(
                f"Expected AssetManager, SpriteSheet, or pygame.Surface, got {type(asset_manager_or_sheet)}"
            )

        frames = sheet.get_frames_grid(
            cols=cols,
            rows=rows,
            frame_count=frame_count,
            scale_size=scale_size,
        )
        anim = Animation(frames, fps=fps, loop=loop)
        return cls(animations={animation_name: anim}, default_animation=animation_name)


# ----------------------------------------------------------------------
# Convenience factory functions
# ----------------------------------------------------------------------

def load_spritesheet(
    asset_manager: "AssetManager",
    key: str,
    alpha: bool = True,
) -> SpriteSheet:
    """Load and return a ``SpriteSheet`` using ``AssetManager``."""
    return SpriteSheet.from_asset(asset_manager, key, alpha=alpha)


def load_animation(
    asset_manager: "AssetManager",
    key: str,
    cols: int,
    rows: int,
    fps: float = 12.0,
    loop: bool = True,
    frame_count: int | None = None,
    scale_size: tuple[int, int] | None = None,
    alpha: bool = True,
) -> Animation:
    """Extract frames from a sprite sheet grid and return an ``Animation``."""
    sheet = load_spritesheet(asset_manager, key, alpha=alpha)
    frames = sheet.get_frames_grid(
        cols=cols,
        rows=rows,
        frame_count=frame_count,
        scale_size=scale_size,
    )
    return Animation(frames, fps=fps, loop=loop)


def load_sprite(
    asset_manager: "AssetManager",
    key: str,
    cols: int = 1,
    rows: int = 1,
    fps: float = 12.0,
    loop: bool = True,
    frame_count: int | None = None,
    scale_size: tuple[int, int] | None = None,
    animation_name: str = "default",
    alpha: bool = True,
) -> Sprite:
    """Load a sprite sheet grid and return a ready-to-use ``Sprite``."""
    return Sprite.from_grid(
        asset_manager,
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
