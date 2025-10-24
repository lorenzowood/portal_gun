"""Tests for universe code manager."""

import pytest
from universe_code import UniverseCode


class TestUniverseCodeParsing:
    """Test parsing universe codes"""

    def test_parse_c137(self):
        """Test parsing C137"""
        uc = UniverseCode("C137")
        assert uc.letter == 'C'
        assert uc.number == 137

    def test_parse_a000(self):
        """Test parsing A000"""
        uc = UniverseCode("A000")
        assert uc.letter == 'A'
        assert uc.number == 0

    def test_parse_f999(self):
        """Test parsing F999"""
        uc = UniverseCode("F999")
        assert uc.letter == 'F'
        assert uc.number == 999

    def test_parse_lowercase(self):
        """Test parsing accepts lowercase"""
        uc = UniverseCode("d456")
        assert uc.letter == 'D'
        assert uc.number == 456

    def test_invalid_letter(self):
        """Test invalid letter raises error"""
        with pytest.raises(ValueError):
            UniverseCode("G123")  # G not in A-F

    def test_invalid_number(self):
        """Test invalid number raises error"""
        with pytest.raises(ValueError):
            UniverseCode("C1000")  # Too many digits

    def test_invalid_format(self):
        """Test invalid format raises error"""
        with pytest.raises(ValueError):
            UniverseCode("12C3")  # Wrong format


class TestUniverseCodeFormatting:
    """Test formatting universe codes"""

    def test_format_c137(self):
        """Test formatting C137"""
        uc = UniverseCode("C137")
        assert str(uc) == "C137"

    def test_format_a000(self):
        """Test formatting with leading zeros"""
        uc = UniverseCode("A000")
        assert str(uc) == "A000"

    def test_format_f009(self):
        """Test formatting with leading zeros in middle"""
        uc = UniverseCode("F009")
        assert str(uc) == "F009"


class TestUniverseCodeIncrement:
    """Test incrementing universe codes"""

    def test_increment_simple(self):
        """Test simple increment"""
        uc = UniverseCode("C137")
        uc.increment()
        assert str(uc) == "C138"

    def test_increment_at_999(self):
        """Test increment rolls to next letter"""
        uc = UniverseCode("C999")
        uc.increment()
        assert str(uc) == "D000"

    def test_increment_at_f999(self):
        """Test increment at F999 wraps to A000"""
        uc = UniverseCode("F999")
        uc.increment()
        assert str(uc) == "A000"

    def test_increment_multiple(self):
        """Test multiple increments"""
        uc = UniverseCode("C137")
        for _ in range(5):
            uc.increment()
        assert str(uc) == "C142"

    def test_increment_across_boundary(self):
        """Test increment across letter boundary"""
        uc = UniverseCode("C998")
        uc.increment()
        assert str(uc) == "C999"
        uc.increment()
        assert str(uc) == "D000"


class TestUniverseCodeDecrement:
    """Test decrementing universe codes"""

    def test_decrement_simple(self):
        """Test simple decrement"""
        uc = UniverseCode("C137")
        uc.decrement()
        assert str(uc) == "C136"

    def test_decrement_at_000(self):
        """Test decrement rolls to previous letter"""
        uc = UniverseCode("C000")
        uc.decrement()
        assert str(uc) == "B999"

    def test_decrement_at_a000(self):
        """Test decrement at A000 wraps to F999"""
        uc = UniverseCode("A000")
        uc.decrement()
        assert str(uc) == "F999"

    def test_decrement_multiple(self):
        """Test multiple decrements"""
        uc = UniverseCode("C142")
        for _ in range(5):
            uc.decrement()
        assert str(uc) == "C137"

    def test_decrement_across_boundary(self):
        """Test decrement across letter boundary"""
        uc = UniverseCode("D001")
        uc.decrement()
        assert str(uc) == "D000"
        uc.decrement()
        assert str(uc) == "C999"


class TestUniverseCodeEdgeCases:
    """Test edge cases and round-trips"""

    def test_increment_decrement_roundtrip(self):
        """Test increment then decrement returns to original"""
        uc = UniverseCode("C137")
        uc.increment()
        uc.decrement()
        assert str(uc) == "C137"

    def test_full_wrap_around(self):
        """Test complete wraparound"""
        uc = UniverseCode("F999")
        uc.increment()  # → A000
        assert str(uc) == "A000"
        uc.decrement()  # → F999
        assert str(uc) == "F999"

    def test_letter_range(self):
        """Test all valid letters"""
        for letter in 'ABCDEF':
            uc = UniverseCode(f"{letter}000")
            assert uc.letter == letter
            assert str(uc) == f"{letter}000"


class TestUniverseCodeCharacterEdit:
    """Test editing individual characters"""

    def test_set_letter(self):
        """Test setting letter"""
        uc = UniverseCode("C137")
        uc.set_letter('D')
        assert str(uc) == "D137"

    def test_set_letter_lowercase(self):
        """Test setting letter with lowercase"""
        uc = UniverseCode("C137")
        uc.set_letter('e')
        assert str(uc) == "E137"

    def test_set_digit(self):
        """Test setting individual digit"""
        uc = UniverseCode("C137")
        uc.set_digit(0, 5)  # First digit
        assert str(uc) == "C537"
        uc.set_digit(1, 9)  # Second digit
        assert str(uc) == "C597"
        uc.set_digit(2, 0)  # Third digit
        assert str(uc) == "C590"

    def test_increment_letter(self):
        """Test incrementing just the letter"""
        uc = UniverseCode("C137")
        uc.increment_letter()
        assert str(uc) == "D137"

    def test_increment_letter_wraps(self):
        """Test incrementing letter wraps at F"""
        uc = UniverseCode("F137")
        uc.increment_letter()
        assert str(uc) == "A137"

    def test_decrement_letter(self):
        """Test decrementing just the letter"""
        uc = UniverseCode("C137")
        uc.decrement_letter()
        assert str(uc) == "B137"

    def test_decrement_letter_wraps(self):
        """Test decrementing letter wraps at A"""
        uc = UniverseCode("A137")
        uc.decrement_letter()
        assert str(uc) == "F137"

    def test_increment_digit(self):
        """Test incrementing individual digit"""
        uc = UniverseCode("C137")
        uc.increment_digit(2)  # Last digit
        assert str(uc) == "C138"

    def test_increment_digit_wraps(self):
        """Test incrementing digit wraps at 9"""
        uc = UniverseCode("C137")
        uc.increment_digit(2)  # 7→8
        uc.increment_digit(2)  # 8→9
        uc.increment_digit(2)  # 9→0
        assert str(uc) == "C130"

    def test_decrement_digit(self):
        """Test decrementing individual digit"""
        uc = UniverseCode("C137")
        uc.decrement_digit(2)  # Last digit
        assert str(uc) == "C136"

    def test_decrement_digit_wraps(self):
        """Test decrementing digit wraps at 0"""
        uc = UniverseCode("C130")
        uc.decrement_digit(2)  # 0→9
        assert str(uc) == "C139"
