"""Tests for animation engine."""

import pytest
from tests.mocks import mock_time
from config import Config


# Import will fail initially - that's expected for TDD
try:
    from animations import (
        Animation,
        AnimationCompositor,
        GentleMotionAnimation,
        SparkleAnimation,
        add_colors,
        clamp_color
    )
except ImportError:
    pass


class TestColorOperations:
    """Test color manipulation functions"""

    def test_add_colors(self):
        """Test adding two RGB colors"""
        result = add_colors((10, 20, 30), (5, 10, 15))
        assert result == (15, 30, 45)

    def test_add_colors_clamping(self):
        """Test colors are clamped at 100"""
        result = add_colors((80, 90, 100), (40, 30, 20))
        assert result == (100, 100, 100)

    def test_clamp_color(self):
        """Test clamping individual color"""
        assert clamp_color((50, 60, 70)) == (50, 60, 70)
        assert clamp_color((110, -10, 50)) == (100, 0, 50)


class TestAnimation:
    """Test base animation class"""

    def test_animation_creation(self):
        """Test creating base animation"""
        anim = Animation(num_pixels=15)
        assert anim.num_pixels == 15
        assert not anim.is_finished()

    def test_animation_start(self):
        """Test starting animation records start time"""
        anim = Animation(num_pixels=15)
        anim.start()
        assert anim.start_time is not None

    def test_animation_finish(self):
        """Test finishing animation"""
        anim = Animation(num_pixels=15)
        anim.finish()
        assert anim.is_finished()

    def test_animation_get_pixels(self):
        """Test getting pixel state"""
        anim = Animation(num_pixels=15)
        anim.start()
        pixels = anim.get_pixels()
        assert len(pixels) == 15
        # Base class returns all black
        assert all(p == (0, 0, 0) for p in pixels)


class TestAnimationCompositor:
    """Test animation compositor"""

    def test_compositor_creation(self):
        """Test creating compositor"""
        comp = AnimationCompositor(num_pixels=15)
        assert comp.num_pixels == 15

    def test_compositor_no_animations(self):
        """Test compositor with no animations"""
        comp = AnimationCompositor(num_pixels=15)
        pixels = comp.get_composite()
        assert len(pixels) == 15
        assert all(p == (0, 0, 0) for p in pixels)

    def test_compositor_single_animation(self):
        """Test compositor with one animation"""
        comp = AnimationCompositor(num_pixels=3)
        anim = Animation(num_pixels=3)
        anim.start()
        # Manually set some pixels for testing
        anim._pixels = [(10, 0, 0), (0, 20, 0), (0, 0, 30)]

        comp.add_animation(anim)
        pixels = comp.get_composite()
        assert pixels[0] == (10, 0, 0)
        assert pixels[1] == (0, 20, 0)
        assert pixels[2] == (0, 0, 30)

    def test_compositor_additive_blending(self):
        """Test additive blending of multiple animations"""
        comp = AnimationCompositor(num_pixels=3)

        anim1 = Animation(num_pixels=3)
        anim1.start()
        anim1._pixels = [(10, 20, 30), (5, 5, 5), (0, 0, 0)]

        anim2 = Animation(num_pixels=3)
        anim2.start()
        anim2._pixels = [(5, 10, 15), (10, 10, 10), (100, 100, 100)]

        comp.add_animation(anim1)
        comp.add_animation(anim2)

        pixels = comp.get_composite()
        assert pixels[0] == (15, 30, 45)
        assert pixels[1] == (15, 15, 15)
        assert pixels[2] == (100, 100, 100)

    def test_compositor_removes_finished(self):
        """Test compositor removes finished animations"""
        comp = AnimationCompositor(num_pixels=3)

        anim1 = Animation(num_pixels=3)
        anim1.start()
        anim1.finish()

        anim2 = Animation(num_pixels=3)
        anim2.start()
        anim2._pixels = [(10, 0, 0), (0, 10, 0), (0, 0, 10)]

        comp.add_animation(anim1)
        comp.add_animation(anim2)

        pixels = comp.get_composite()
        # Should only show anim2 (anim1 is finished)
        assert pixels[0] == (10, 0, 0)


class TestGentleMotionAnimation:
    """Test gentle motion animation"""

    def test_gentle_motion_creation(self):
        """Test creating gentle motion animation"""
        anim = GentleMotionAnimation(
            num_pixels=15,
            center_pixel=7,
            max_brightness=50,
            color=(0, 100, 0),
            ramp_up_ms=3000,
            hold_ms=1000,
            ramp_down_ms=3000,
            decay_pixels=2,
            decay_rate=0.5
        )
        assert anim.center_pixel == 7
        assert not anim.is_finished()

    def test_gentle_motion_timing(self):
        """Test gentle motion follows timing correctly"""
        mock_time.reset()

        anim = GentleMotionAnimation(
            num_pixels=15,
            center_pixel=7,
            max_brightness=50,
            color=(0, 100, 0),
            ramp_up_ms=1000,
            hold_ms=500,
            ramp_down_ms=1000,
            decay_pixels=1,
            decay_rate=0.5
        )

        anim.start()

        # At t=0, should be at 0%
        pixels = anim.get_pixels()
        assert pixels[7] == (0, 0, 0)  # Center pixel

        # At t=500ms (50% through ramp up), center should be ~25% of 50%
        mock_time.advance(500)
        anim.update()
        pixels = anim.get_pixels()
        # Center pixel should have some green
        assert pixels[7][1] > 0
        assert pixels[7][1] < 50  # Less than max

        # At t=1000ms (end of ramp up), should be at max
        mock_time.advance(500)
        anim.update()
        pixels = anim.get_pixels()
        # Should be at or near max brightness
        assert pixels[7][1] >= 45  # Allow small margin

        # Should not be finished yet
        assert not anim.is_finished()

        # At end of animation
        mock_time.advance(1500)  # Through hold and ramp down
        anim.update()
        assert anim.is_finished()

    def test_gentle_motion_decay(self):
        """Test gentle motion decay to adjacent pixels"""
        mock_time.reset()

        anim = GentleMotionAnimation(
            num_pixels=15,
            center_pixel=7,
            max_brightness=100,
            color=(0, 100, 0),
            ramp_up_ms=100,
            hold_ms=0,
            ramp_down_ms=100,
            decay_pixels=2,
            decay_rate=0.5
        )

        anim.start()
        mock_time.advance(100)  # End of ramp up
        anim.update()

        pixels = anim.get_pixels()
        center_brightness = pixels[7][1]
        adjacent1_brightness = pixels[6][1]
        adjacent2_brightness = pixels[5][1]

        # Check decay pattern
        assert center_brightness >= 95  # Center should be ~100%
        assert adjacent1_brightness < center_brightness
        assert adjacent2_brightness < adjacent1_brightness


class TestSparkleAnimation:
    """Test sparkle animation"""

    def test_sparkle_creation(self):
        """Test creating sparkle animation"""
        anim = SparkleAnimation(
            num_pixels=15,
            pixel_index=5,
            max_brightness=100,
            color=(94, 94, 100),
            ramp_up_ms=20,
            hold_ms=0,
            ramp_down_ms=500
        )
        assert anim.pixel_index == 5
        assert not anim.is_finished()

    def test_sparkle_timing(self):
        """Test sparkle follows timing"""
        mock_time.reset()

        anim = SparkleAnimation(
            num_pixels=15,
            pixel_index=5,
            max_brightness=100,
            color=(100, 100, 100),
            ramp_up_ms=10,
            hold_ms=10,
            ramp_down_ms=100
        )

        anim.start()

        # At ramp up
        mock_time.advance(10)
        anim.update()
        pixels = anim.get_pixels()
        assert pixels[5][0] >= 90  # Should be near max

        # During hold
        mock_time.advance(5)
        anim.update()
        pixels = anim.get_pixels()
        assert pixels[5][0] >= 90  # Should stay high

        # During ramp down
        mock_time.advance(60)  # Partway through ramp down
        anim.update()
        pixels = anim.get_pixels()
        assert 0 < pixels[5][0] < 90  # Should be fading

        # Finished
        mock_time.advance(50)
        anim.update()
        assert anim.is_finished()

    def test_sparkle_only_affects_one_pixel(self):
        """Test sparkle only affects its pixel"""
        mock_time.reset()

        anim = SparkleAnimation(
            num_pixels=15,
            pixel_index=7,
            max_brightness=100,
            color=(100, 100, 100),
            ramp_up_ms=10,
            hold_ms=0,
            ramp_down_ms=10
        )

        anim.start()
        mock_time.advance(10)
        anim.update()

        pixels = anim.get_pixels()
        # Only pixel 7 should be lit
        for i in range(15):
            if i == 7:
                assert pixels[i][0] > 0
            else:
                assert pixels[i] == (0, 0, 0)
