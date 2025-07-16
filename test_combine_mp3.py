#!/usr/bin/env python3
"""
Unit tests for the combine_mp3.py script, specifically testing the
find_mp3_groups function.
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
        """
        Test basic grouping of MP3 files using directory name as base name.
        """
        test_files = [
            "Der Aufstieg des Erddrachen - 01.mp3",
            "Der Aufstieg des Erddrachen - 02.mp3",
            "Der Aufstieg des Erddrachen - 03.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)

        self.assertEqual(len(groups), 1)
        directory_name = os.path.basename(self.test_dir)
        self.assertIn(directory_name, groups)
        self.assertEqual(len(groups[directory_name]), 3)

    def test_multiple_groups(self):
        """
        Test that all numbered MP3 files in a directory are grouped together.
        """
        test_files = [
            "Story A - 01.mp3",
            "Story A - 02.mp3",
            "Story B - 01.mp3",
            "Story B - 02.mp3",
            "Story B - 03.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)

        # All files grouped under directory name
        self.assertEqual(len(groups), 1)
        directory_name = os.path.basename(self.test_dir)
        self.assertIn(directory_name, groups)
        # All 5 files together
        self.assertEqual(len(groups[directory_name]), 5)

    def test_single_file_excluded(self):
        """Test that directories with only one numbered file are excluded."""
        test_files = [
            "Single File - 01.mp3"  # Only one file, should be excluded
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)

        self.assertEqual(len(groups), 0)  # No groups since only one file

    def test_different_number_formats(self):
        """
        Test different number formats (with/without leading zeros, spaces).
        """
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

        # All files grouped under directory name
        self.assertEqual(len(groups), 1)
        directory_name = os.path.basename(self.test_dir)
        self.assertIn(directory_name, groups)
        # All 7 files together
        self.assertEqual(len(groups[directory_name]), 7)

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
        directory_name = os.path.basename(self.test_dir)
        self.assertIn(directory_name, groups)
        self.assertEqual(len(groups[directory_name]), 3)

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
        directory_name = os.path.basename(self.test_dir)
        self.assertIn(directory_name, groups)
        # Only the 2 MP3 files
        self.assertEqual(len(groups[directory_name]), 2)

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
        directory_name = os.path.basename(self.test_dir)
        self.assertIn(directory_name, groups)
        # Only the 2 numbered files
        self.assertEqual(len(groups[directory_name]), 2)

    def test_empty_directory(self):
        """Test behavior with empty directory."""
        groups = find_mp3_groups(self.test_dir)

        self.assertEqual(len(groups), 0)
        self.assertEqual(groups, {})

    def test_long_base_names(self):
        """Test with very long base names."""
        test_files = [
            ("This is a Very Long Story Title with Many Words"
                " and Characters - 01.mp3"),
            ("This is a Very Long Story Title with Many Words"
                " and Characters - 02.mp3")
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)

        self.assertEqual(len(groups), 1)
        directory_name = os.path.basename(self.test_dir)
        self.assertIn(directory_name, groups)
        self.assertEqual(len(groups[directory_name]), 2)

    def test_special_characters_in_names(self):
        """Test with special characters in base names."""
        test_files = [
            "Story with (Parentheses) & Symbols! - 01.mp3",
            "Story with (Parentheses) & Symbols! - 02.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)

        self.assertEqual(len(groups), 1)
        directory_name = os.path.basename(self.test_dir)
        self.assertIn(directory_name, groups)
        self.assertEqual(len(groups[directory_name]), 2)

    def test_full_file_paths_returned(self):
        """Test that full file paths are returned, not just filenames."""
        test_files = [
            "Path Test - 01.mp3",
            "Path Test - 02.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)

        self.assertEqual(len(groups), 1)
        directory_name = os.path.basename(self.test_dir)
        file_paths = groups[directory_name]

        for file_path in file_paths:
            self.assertTrue(os.path.isabs(file_path))
            self.assertTrue(file_path.startswith(self.test_dir))
            self.assertTrue(os.path.exists(file_path))

    def test_numbers_at_beginning_of_filename(self):
        """Test files with numbers at the beginning of the filename."""
        test_files = [
            "01 - Chapter One.mp3",
            "02 - Chapter Two.mp3",
            "03 - Chapter Three.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)

        self.assertEqual(len(groups), 1)
        directory_name = os.path.basename(self.test_dir)
        self.assertIn(directory_name, groups)
        self.assertEqual(len(groups[directory_name]), 3)

    def test_mixed_number_positions(self):
        """Test files with numbers at both beginning and end positions."""
        test_files = [
            "01 - Chapter One.mp3",
            "Story - 02.mp3",
            "03 - Chapter Three.mp3",
            "Story - 04.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)

        self.assertEqual(len(groups), 1)
        directory_name = os.path.basename(self.test_dir)
        self.assertIn(directory_name, groups)
        self.assertEqual(len(groups[directory_name]), 4)

    def test_sorting_with_numbers_at_beginning(self):
        """Test that files with numbers at beginning are sorted correctly."""
        test_files = [
            "03 - Chapter Three.mp3",
            "01 - Chapter One.mp3",
            "02 - Chapter Two.mp3",
            "10 - Chapter Ten.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)
        directory_name = os.path.basename(self.test_dir)

        # Import the sorting function to test it directly
        from combine_mp3 import sort_mp3_files
        sorted_files = sort_mp3_files(groups[directory_name])

        # Extract just the filenames for easier assertion
        filenames = [os.path.basename(f) for f in sorted_files]
        expected_order = [
            "01 - Chapter One.mp3",
            "02 - Chapter Two.mp3",
            "03 - Chapter Three.mp3",
            "10 - Chapter Ten.mp3"
        ]

        self.assertEqual(filenames, expected_order)


class TestProcessDirectoryEdgeCases(unittest.TestCase):
    """Test cases for edge cases that cause 'No MP3 groups found' messages."""

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

    def test_directory_with_no_mp3_files(self):
        """Test directory with no MP3 files at all."""
        test_files = [
            "document.txt",
            "image.jpg",
            "video.mp4"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)
        self.assertEqual(len(groups), 0)
        self.assertEqual(groups, {})

    def test_directory_with_only_unnumbered_mp3_files(self):
        """Test directory with MP3 files that don't have numbers."""
        test_files = [
            "audio_file.mp3",
            "another_audio.mp3",
            "music.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)
        self.assertEqual(len(groups), 0)
        self.assertEqual(groups, {})

    def test_directory_with_single_numbered_mp3_file(self):
        """Test directory with only one numbered MP3 file."""
        test_files = [
            "Story - 01.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)
        self.assertEqual(len(groups), 0)
        self.assertEqual(groups, {})

    def test_directory_with_mixed_numbered_and_unnumbered_mp3_files(self):
        """
        Test directory with mix of numbered and unnumbered MP3 files but
        only one numbered.
        """
        test_files = [
            "Story - 01.mp3",  # Only one numbered file
            "music.mp3",       # Unnumbered files
            "audio.mp3",
            "sound.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)
        self.assertEqual(len(groups), 0)
        self.assertEqual(groups, {})

    def test_directory_with_wrong_number_format(self):
        """Test directory with MP3 files that have wrong number formats."""
        test_files = [
            "Story Part 1.mp3",     # Space before number, no dash
            "Story Part 2.mp3",     # Space before number, no dash
            "Story (01).mp3",       # Parentheses around number
            "Story (02).mp3",       # Parentheses around number
            "Story_01.mp3",         # Underscore instead of dash
            "Story_02.mp3"          # Underscore instead of dash
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)
        self.assertEqual(len(groups), 0)
        self.assertEqual(groups, {})

    def test_directory_with_numbers_in_middle_of_filename(self):
        """
        Test directory with numbers in middle of filename (not at beginning or
        end).
        """
        test_files = [
            "Story 01 Chapter.mp3",
            "Story 02 Chapter.mp3",
            "Story 03 Chapter.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)
        self.assertEqual(len(groups), 0)
        self.assertEqual(groups, {})

    def test_directory_with_no_dash_separator(self):
        """Test directory with numbers but no dash separator."""
        test_files = [
            "Story 01.mp3",
            "Story 02.mp3",
            "Story 03.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)
        self.assertEqual(len(groups), 0)
        self.assertEqual(groups, {})

    def test_directory_with_special_characters_breaking_pattern(self):
        """
        Test directory with special characters that break the expected pattern.
        """
        test_files = [
            "Story@01.mp3",
            "Story@02.mp3",
            "Story#01.mp3",
            "Story#02.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)
        self.assertEqual(len(groups), 0)
        self.assertEqual(groups, {})

    def test_directory_with_existing_combined_file(self):
        """
        Test directory that already has a combined file but no source files.
        """
        test_files = [
            "Final Story.mp3",  # Already combined file
            "readme.txt"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)
        self.assertEqual(len(groups), 0)
        self.assertEqual(groups, {})

    def test_directory_with_broken_encoding_filenames(self):
        """
        Test directory with files that have encoding issues in their names.
        """
        test_files = [
            "Story├╝ - 01.mp3",  # Unicode characters that might cause issues
            "Story├╝ - 02.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)
        # This should still work as the pattern matching should handle it
        self.assertEqual(len(groups), 1)
        directory_name = os.path.basename(self.test_dir)
        self.assertIn(directory_name, groups)
        self.assertEqual(len(groups[directory_name]), 2)

    def test_directory_with_period_number_format(self):
        """
        Test directory with files that start with 'NN. ' format
        instead of 'NN - '.
        """
        test_files = [
            "01. Tracey West - Track 1 - Story Title.mp3",
            "02. Tracey West - Track 2 - Story Title.mp3",
            "03. Tracey West - Track 3 - Story Title.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)
        # This should work after fixing the regex to handle 'NN. ' format
        self.assertEqual(len(groups), 1)
        directory_name = os.path.basename(self.test_dir)
        self.assertIn(directory_name, groups)
        self.assertEqual(len(groups[directory_name]), 3)

    def test_directory_with_complex_track_naming(self):
        """
        Test directory with complex track naming like real audiobook files.
        """
        test_files = [
            "01. Author Name - Track 1 - Book Title - Series Info.mp3",
            "02. Author Name - Track 2 - Book Title - Series Info.mp3",
            "03. Author Name - Track 3 - Book Title - Series Info.mp3",
            "04. Author Name - Track 4 - Book Title - Series Info.mp3",
            "05. Author Name - Track 5 - Book Title - Series Info.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)
        # This should work after fixing the regex to handle 'NN. ' format
        self.assertEqual(len(groups), 1)
        directory_name = os.path.basename(self.test_dir)
        self.assertIn(directory_name, groups)
        self.assertEqual(len(groups[directory_name]), 5)

    def test_directory_with_mixed_period_and_dash_formats(self):
        """Test directory with mix of 'NN. ' and 'NN - ' formats."""
        test_files = [
            "01. Story Title Part One.mp3",  # Period format
            "02 - Story Title Part Two.mp3",  # Dash format
            "03. Story Title Part Three.mp3"  # Period format
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)
        # After fixing, both formats should be recognized
        self.assertEqual(len(groups), 1)
        directory_name = os.path.basename(self.test_dir)
        self.assertIn(directory_name, groups)
        self.assertEqual(len(groups[directory_name]), 3)

    def test_directory_with_leading_zeros_period_format(self):
        """Test directory with leading zeros in period format."""
        test_files = [
            "001. Story Chapter One.mp3",
            "002. Story Chapter Two.mp3",
            "010. Story Chapter Ten.mp3"
        ]
        self.create_test_files(test_files)

        groups = find_mp3_groups(self.test_dir)
        # This should work after fixing the regex to handle 'NN. ' format
        self.assertEqual(len(groups), 1)
        directory_name = os.path.basename(self.test_dir)
        self.assertIn(directory_name, groups)
        self.assertEqual(len(groups[directory_name]), 3)


if __name__ == "__main__":
    unittest.main()
