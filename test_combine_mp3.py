#!/usr/bin/env python3
"""
Unit tests for the combine_mp3.py script, specifically testing the find_mp3_groups function.
"""

import os
import tempfile
import unittest
from pathlib import Path
from combine_mp3 import find_mp3_groups


class TestFindMp3Groups(unittest.TestCase):
    """Test cases for the find_mp3_groups function."""

    def setUp(self):
        """Set up a temporary directory for testing."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory after tests."""
        import shutil
        shutil.rmtree(self.test_dir)

    def create_test_files(self, filenames):
        """Create empty test files in the test directory."""
        for filename in filenames:
            file_path = os.path.join(self.test_dir, filename)
            Path(file_path).touch()

    def test_basic_grouping(self):
        """Test basic grouping of MP3 files with same base name."""
        test_files = [
            "Der Aufstieg des Erddrachen - 01.mp3",
            "Der Aufstieg des Erddrachen - 02.mp3",
            "Der Aufstieg des Erddrachen - 03.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)

        self.assertEqual(len(groups), 1)
        self.assertIn("Der Aufstieg des Erddrachen", groups)
        self.assertEqual(len(groups["Der Aufstieg des Erddrachen"]), 3)

    def test_multiple_groups(self):
        """Test grouping of multiple different MP3 series."""
        test_files = [
            "Story A - 01.mp3",
            "Story A - 02.mp3",
            "Story B - 01.mp3",
            "Story B - 02.mp3",
            "Story B - 03.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)

        self.assertEqual(len(groups), 2)
        self.assertIn("Story A", groups)
        self.assertIn("Story B", groups)
        self.assertEqual(len(groups["Story A"]), 2)
        self.assertEqual(len(groups["Story B"]), 3)

    def test_single_file_excluded(self):
        """Test that single files (no grouping) are excluded."""
        test_files = [
            "Single File - 01.mp3",
            "Story A - 01.mp3",
            "Story A - 02.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)

        self.assertEqual(len(groups), 1)
        self.assertIn("Story A", groups)
        self.assertNotIn("Single File", groups)

    def test_different_number_formats(self):
        """Test different number formats (with/without leading zeros, spaces)."""
        test_files = [
            "Test Story - 1.mp3",
            "Test Story - 2.mp3",
            "Test Story - 10.mp3",
            "Padded Story - 01.mp3",
            "Padded Story - 02.mp3",
            "Spaced Story -1.mp3",
            "Spaced Story -2.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)

        self.assertEqual(len(groups), 3)
        self.assertIn("Test Story", groups)
        self.assertIn("Padded Story", groups)
        self.assertIn("Spaced Story", groups)

    def test_case_insensitive_extension(self):
        """Test that .MP3 and .mp3 extensions are both recognized."""
        test_files = [
            "Mixed Case - 01.mp3",
            "Mixed Case - 02.MP3",
            "Mixed Case - 03.Mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)

        self.assertEqual(len(groups), 1)
        self.assertIn("Mixed Case", groups)
        self.assertEqual(len(groups["Mixed Case"]), 3)

    def test_non_mp3_files_ignored(self):
        """Test that non-MP3 files are ignored."""
        test_files = [
            "Audio Story - 01.mp3",
            "Audio Story - 02.mp3",
            "Audio Story - 01.wav",
            "Audio Story - 02.txt",
            "readme.txt"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)

        self.assertEqual(len(groups), 1)
        self.assertIn("Audio Story", groups)
        self.assertEqual(len(groups["Audio Story"]), 2)

    def test_files_without_numbers_ignored(self):
        """Test that MP3 files without numbers are ignored."""
        test_files = [
            "Numbered Story - 01.mp3",
            "Numbered Story - 02.mp3",
            "No Numbers Story.mp3",
            "Also No Numbers.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)

        self.assertEqual(len(groups), 1)
        self.assertIn("Numbered Story", groups)
        self.assertEqual(len(groups["Numbered Story"]), 2)

    def test_empty_directory(self):
        """Test behavior with empty directory."""
        groups = find_mp3_groups(self.test_dir)

        self.assertEqual(len(groups), 0)
        self.assertEqual(groups, {})

    def test_long_base_names(self):
        """Test with very long base names."""
        test_files = [
            "This is a Very Long Story Title with Many Words and Characters - 01.mp3",
            "This is a Very Long Story Title with Many Words and Characters - 02.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)

        self.assertEqual(len(groups), 1)
        expected_base = "This is a Very Long Story Title with Many Words and Characters"
        self.assertIn(expected_base, groups)

    def test_special_characters_in_names(self):
        """Test with special characters in base names."""
        test_files = [
            "Story with (Parentheses) & Symbols! - 01.mp3",
            "Story with (Parentheses) & Symbols! - 02.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)

        self.assertEqual(len(groups), 1)
        expected_base = "Story with (Parentheses) & Symbols!"
        self.assertIn(expected_base, groups)

    def test_full_file_paths_returned(self):
        """Test that full file paths are returned, not just filenames."""
        test_files = [
            "Path Test - 01.mp3",
            "Path Test - 02.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)

        self.assertEqual(len(groups), 1)
        file_paths = groups["Path Test"]

        for file_path in file_paths:
            self.assertTrue(os.path.isabs(file_path))
            self.assertTrue(file_path.startswith(self.test_dir))
            self.assertTrue(os.path.exists(file_path))


if __name__ == "__main__":
    unittest.main()
