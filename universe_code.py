"""Universe code manager for Portal Gun.

Handles universe code operations like C137, A000-F999.
Pure logic, no hardware dependencies.
"""

import re


class UniverseCode:
    """Manages universe code format and operations"""

    VALID_LETTERS = 'ABCDEF'
    PATTERN = re.compile(r'^([A-Fa-f])(\d{3})$')

    def __init__(self, code):
        """
        Initialize with a universe code string

        Args:
            code: String like "C137"

        Raises:
            ValueError: If code format is invalid
        """
        match = self.PATTERN.match(code)
        if not match:
            raise ValueError(f"Invalid universe code format: {code}")

        self.letter = match.group(1).upper()
        self.number = int(match.group(2))

        if self.letter not in self.VALID_LETTERS:
            raise ValueError(f"Invalid letter: {self.letter}")
        if not (0 <= self.number <= 999):
            raise ValueError(f"Invalid number: {self.number}")

    def __str__(self):
        """Format as string like C137"""
        return f"{self.letter}{self.number:03d}"

    def increment(self):
        """Increment universe code (C137→C138, C999→D000, F999→A000)"""
        self.number += 1
        if self.number > 999:
            self.number = 0
            self.increment_letter()

    def decrement(self):
        """Decrement universe code (C137→C136, C000→B999, A000→F999)"""
        self.number -= 1
        if self.number < 0:
            self.number = 999
            self.decrement_letter()

    def increment_letter(self):
        """Increment just the letter (C→D, F→A)"""
        idx = self.VALID_LETTERS.index(self.letter)
        idx = (idx + 1) % len(self.VALID_LETTERS)
        self.letter = self.VALID_LETTERS[idx]

    def decrement_letter(self):
        """Decrement just the letter (C→B, A→F)"""
        idx = self.VALID_LETTERS.index(self.letter)
        idx = (idx - 1) % len(self.VALID_LETTERS)
        self.letter = self.VALID_LETTERS[idx]

    def set_letter(self, letter):
        """
        Set the letter

        Args:
            letter: Single character A-F (case insensitive)

        Raises:
            ValueError: If letter not in A-F
        """
        letter = letter.upper()
        if letter not in self.VALID_LETTERS:
            raise ValueError(f"Invalid letter: {letter}")
        self.letter = letter

    def set_digit(self, position, value):
        """
        Set a specific digit (0=hundreds, 1=tens, 2=ones)

        Args:
            position: 0-2 for digit position
            value: 0-9 for digit value

        Raises:
            ValueError: If position or value invalid
        """
        if not (0 <= position <= 2):
            raise ValueError(f"Invalid position: {position}")
        if not (0 <= value <= 9):
            raise ValueError(f"Invalid digit value: {value}")

        # Convert to string, replace digit, convert back
        num_str = f"{self.number:03d}"
        digits = list(num_str)
        digits[position] = str(value)
        self.number = int(''.join(digits))

    def increment_digit(self, position):
        """
        Increment a specific digit (wraps 9→0)

        Args:
            position: 0-2 for digit position
        """
        num_str = f"{self.number:03d}"
        digit = int(num_str[position])
        digit = (digit + 1) % 10
        self.set_digit(position, digit)

    def decrement_digit(self, position):
        """
        Decrement a specific digit (wraps 0→9)

        Args:
            position: 0-2 for digit position
        """
        num_str = f"{self.number:03d}"
        digit = int(num_str[position])
        digit = (digit - 1) % 10
        self.set_digit(position, digit)

    def get_digit(self, position):
        """
        Get a specific digit value

        Args:
            position: 0-2 for digit position

        Returns:
            Digit value 0-9
        """
        num_str = f"{self.number:03d}"
        return int(num_str[position])
