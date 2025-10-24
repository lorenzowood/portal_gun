"""Animation engine for Portal Gun neopixels.

Provides time-based animations with additive compositing.
All colors use percentage values (0-100).
"""

import time
import random


def clamp_color(color):
    """
    Clamp RGB color values to 0-100 range

    Args:
        color: RGB tuple (percentages)

    Returns:
        Clamped RGB tuple
    """
    return tuple(max(0, min(100, c)) for c in color)


def add_colors(color1, color2):
    """
    Add two RGB colors with clamping

    Args:
        color1: RGB tuple (percentages)
        color2: RGB tuple (percentages)

    Returns:
        Summed and clamped RGB tuple
    """
    result = tuple(c1 + c2 for c1, c2 in zip(color1, color2))
    return clamp_color(result)


def scale_color(color, scale):
    """
    Scale color by a factor

    Args:
        color: RGB tuple (percentages)
        scale: Scale factor (0.0 to 1.0)

    Returns:
        Scaled RGB tuple
    """
    return tuple(c * scale for c in color)


def lerp(start, end, t):
    """
    Linear interpolation

    Args:
        start: Start value
        end: End value
        t: Interpolation factor (0.0 to 1.0)

    Returns:
        Interpolated value
    """
    return start + (end - start) * t


class Animation:
    """Base animation class"""

    def __init__(self, num_pixels):
        """
        Initialize animation

        Args:
            num_pixels: Number of pixels in strip
        """
        self.num_pixels = num_pixels
        self._pixels = [(0, 0, 0)] * num_pixels
        self.start_time = None
        self._finished = False

    def start(self):
        """Start the animation (records start time)"""
        self.start_time = time.ticks_ms()
        self._finished = False

    def finish(self):
        """Mark animation as finished"""
        self._finished = True

    def is_finished(self):
        """Check if animation is finished"""
        return self._finished

    def get_elapsed_ms(self):
        """Get elapsed time since start in milliseconds"""
        if self.start_time is None:
            return 0
        return time.ticks_diff(time.ticks_ms(), self.start_time)

    def update(self):
        """Update animation state (override in subclasses)"""
        pass

    def get_pixels(self):
        """Get current pixel states"""
        return self._pixels


class AnimationCompositor:
    """Composites multiple animations with additive blending"""

    def __init__(self, num_pixels):
        """
        Initialize compositor

        Args:
            num_pixels: Number of pixels in strip
        """
        self.num_pixels = num_pixels
        self.animations = []

    def add_animation(self, animation):
        """
        Add animation to compositor

        Args:
            animation: Animation instance
        """
        self.animations.append(animation)

    def remove_animation(self, animation):
        """
        Remove animation from compositor

        Args:
            animation: Animation instance
        """
        if animation in self.animations:
            self.animations.remove(animation)

    def clear_animations(self):
        """Remove all animations"""
        self.animations.clear()

    def update(self):
        """Update all animations and remove finished ones"""
        # Update all animations
        for anim in self.animations:
            anim.update()

        # Remove finished animations
        self.animations = [a for a in self.animations if not a.is_finished()]

    def get_composite(self):
        """
        Get composite pixel state from all animations

        Returns:
            List of RGB tuples (percentages)
        """
        # Start with all pixels off
        result = [(0, 0, 0)] * self.num_pixels

        # Additively blend all animations
        for anim in self.animations:
            if not anim.is_finished():
                anim_pixels = anim.get_pixels()
                for i in range(self.num_pixels):
                    result[i] = add_colors(result[i], anim_pixels[i])

        return result


class GentleMotionAnimation(Animation):
    """Gentle wave animation with decay to adjacent pixels"""

    def __init__(self, num_pixels, center_pixel, max_brightness, color,
                 ramp_up_ms, hold_ms, ramp_down_ms, decay_pixels, decay_rate):
        """
        Initialize gentle motion animation

        Args:
            num_pixels: Number of pixels
            center_pixel: Center pixel index
            max_brightness: Maximum brightness (0-100)
            color: RGB color tuple (0-100)
            ramp_up_ms: Ramp up duration
            hold_ms: Hold duration
            ramp_down_ms: Ramp down duration
            decay_pixels: Number of pixels either side affected
            decay_rate: Brightness decay per pixel (0-1)
        """
        super().__init__(num_pixels)
        self.center_pixel = center_pixel
        self.max_brightness = max_brightness
        self.color = color
        self.ramp_up_ms = ramp_up_ms
        self.hold_ms = hold_ms
        self.ramp_down_ms = ramp_down_ms
        self.decay_pixels = decay_pixels
        self.decay_rate = decay_rate

        self.total_duration = ramp_up_ms + hold_ms + ramp_down_ms

    def update(self):
        """Update animation state"""
        elapsed = self.get_elapsed_ms()

        # Check if finished
        if elapsed >= self.total_duration:
            self.finish()
            self._pixels = [(0, 0, 0)] * self.num_pixels
            return

        # Calculate center pixel brightness based on phase
        if elapsed < self.ramp_up_ms:
            # Ramp up
            t = elapsed / self.ramp_up_ms
            brightness = t * self.max_brightness
        elif elapsed < self.ramp_up_ms + self.hold_ms:
            # Hold
            brightness = self.max_brightness
        else:
            # Ramp down
            t = (elapsed - self.ramp_up_ms - self.hold_ms) / self.ramp_down_ms
            brightness = (1 - t) * self.max_brightness

        # Apply to center pixel and decay to adjacent pixels
        for i in range(self.num_pixels):
            distance = abs(i - self.center_pixel)
            if distance <= self.decay_pixels:
                # Calculate decayed brightness
                pixel_brightness = brightness * (self.decay_rate ** distance)
                # Apply to color
                scale = pixel_brightness / 100.0
                self._pixels[i] = scale_color(self.color, scale)
            else:
                self._pixels[i] = (0, 0, 0)


class SparkleAnimation(Animation):
    """Quick sparkle on a single pixel"""

    def __init__(self, num_pixels, pixel_index, max_brightness, color,
                 ramp_up_ms, hold_ms, ramp_down_ms):
        """
        Initialize sparkle animation

        Args:
            num_pixels: Number of pixels
            pixel_index: Which pixel to sparkle
            max_brightness: Maximum brightness (0-100)
            color: RGB color tuple (0-100)
            ramp_up_ms: Ramp up duration
            hold_ms: Hold duration
            ramp_down_ms: Ramp down duration
        """
        super().__init__(num_pixels)
        self.pixel_index = pixel_index
        self.max_brightness = max_brightness
        self.color = color
        self.ramp_up_ms = ramp_up_ms
        self.hold_ms = hold_ms
        self.ramp_down_ms = ramp_down_ms

        self.total_duration = ramp_up_ms + hold_ms + ramp_down_ms

    def update(self):
        """Update animation state"""
        elapsed = self.get_elapsed_ms()

        # Check if finished
        if elapsed >= self.total_duration:
            self.finish()
            self._pixels = [(0, 0, 0)] * self.num_pixels
            return

        # Calculate brightness based on phase
        if elapsed < self.ramp_up_ms:
            # Ramp up
            if self.ramp_up_ms > 0:
                t = elapsed / self.ramp_up_ms
            else:
                t = 1.0
            brightness = t * self.max_brightness
        elif elapsed < self.ramp_up_ms + self.hold_ms:
            # Hold
            brightness = self.max_brightness
        else:
            # Ramp down
            t = (elapsed - self.ramp_up_ms - self.hold_ms) / self.ramp_down_ms
            brightness = (1 - t) * self.max_brightness

        # Apply to single pixel
        scale = brightness / 100.0
        self._pixels = [(0, 0, 0)] * self.num_pixels
        self._pixels[self.pixel_index] = scale_color(self.color, scale)


class SparkleGroupManager:
    """Manages groups of sparkle animations with random timing"""

    def __init__(self, compositor, config):
        """
        Initialize sparkle group manager

        Args:
            compositor: AnimationCompositor instance
            config: Config object
        """
        self.compositor = compositor
        self.config = config
        self.num_pixels = config.NUM_PIXELS
        self.next_sparkle_time = 0
        self.sparkles_in_group = 0
        self.sparkles_remaining = 0
        self.in_group = False

    def update(self):
        """Update sparkle generation"""
        now = time.ticks_ms()

        if not self.in_group:
            # Between groups - check if time to start new group
            if time.ticks_diff(now, self.next_sparkle_time) >= 0:
                # Start new group
                self.sparkles_remaining = random.randint(
                    self.config.SPARKLE_GROUP_MIN,
                    self.config.SPARKLE_GROUP_MAX
                )
                self.in_group = True
                self._create_sparkle()
                # Schedule next sparkle in group
                delay = random.randint(
                    self.config.SPARKLE_WITHIN_GROUP_MIN_MS,
                    self.config.SPARKLE_WITHIN_GROUP_MAX_MS
                )
                self.next_sparkle_time = time.ticks_add(now, delay)
        else:
            # In group - check if time for next sparkle
            if time.ticks_diff(now, self.next_sparkle_time) >= 0:
                self.sparkles_remaining -= 1
                if self.sparkles_remaining > 0:
                    # Create another sparkle in this group
                    self._create_sparkle()
                    delay = random.randint(
                        self.config.SPARKLE_WITHIN_GROUP_MIN_MS,
                        self.config.SPARKLE_WITHIN_GROUP_MAX_MS
                    )
                    self.next_sparkle_time = time.ticks_add(now, delay)
                else:
                    # Group finished, schedule next group
                    self.in_group = False
                    delay = random.randint(
                        self.config.SPARKLE_BETWEEN_GROUPS_MIN_MS,
                        self.config.SPARKLE_BETWEEN_GROUPS_MAX_MS
                    )
                    self.next_sparkle_time = time.ticks_add(now, delay)

    def _create_sparkle(self):
        """Create a new sparkle animation"""
        pixel = random.randint(0, self.num_pixels - 1)
        sparkle = SparkleAnimation(
            num_pixels=self.num_pixels,
            pixel_index=pixel,
            max_brightness=self.config.SPARKLE_MAX_BRIGHTNESS,
            color=self.config.SPARKLE_COLOR,
            ramp_up_ms=self.config.SPARKLE_RAMP_UP_MS,
            hold_ms=self.config.SPARKLE_HOLD_MS,
            ramp_down_ms=self.config.SPARKLE_RAMP_DOWN_MS
        )
        sparkle.start()
        self.compositor.add_animation(sparkle)


class GentleMotionManager:
    """Manages gentle motion animations with timed intervals"""

    def __init__(self, compositor, config):
        """
        Initialize gentle motion manager

        Args:
            compositor: AnimationCompositor instance
            config: Config object
        """
        self.compositor = compositor
        self.config = config
        self.num_pixels = config.NUM_PIXELS
        self.next_motion_time = 0

    def update(self):
        """Update gentle motion generation"""
        now = time.ticks_ms()

        if time.ticks_diff(now, self.next_motion_time) >= 0:
            # Time to create new gentle motion
            pixel = random.randint(0, self.num_pixels - 1)
            motion = GentleMotionAnimation(
                num_pixels=self.num_pixels,
                center_pixel=pixel,
                max_brightness=self.config.GENTLE_MOTION_MAX_BRIGHTNESS,
                color=self.config.GENTLE_MOTION_COLOR,
                ramp_up_ms=self.config.GENTLE_MOTION_RAMP_UP_MS,
                hold_ms=self.config.GENTLE_MOTION_HOLD_MS,
                ramp_down_ms=self.config.GENTLE_MOTION_RAMP_DOWN_MS,
                decay_pixels=self.config.GENTLE_MOTION_DECAY_PIXELS,
                decay_rate=self.config.GENTLE_MOTION_DECAY_RATE
            )
            motion.start()
            self.compositor.add_animation(motion)

            # Schedule next motion
            self.next_motion_time = time.ticks_add(
                now,
                self.config.GENTLE_MOTION_INTERVAL_MS
            )
