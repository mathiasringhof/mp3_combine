#!/usr/bin/env python3
"""
MP3 Concatenation Script

This script traverses directories recursively and combines MP3 files with the same base name
(ignoring numbers) into a single concatenated file using ffmpeg.

Usage:
    python combine_mp3.py <directory>
    python combine_mp3.py /path/to/audiobooks
    python combine_mp3.py "~/Downloads/Audio Files"

Example:
    "Der Aufstieg des Erddrachen - 01.mp3" + "Der Aufstieg des Erddrachen - 02.mp3" + ...
    becomes "Der Aufstieg des Erddrachen.mp3"
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
import warnings


def find_mp3_groups(directory):
    """
    Find MP3 files in a directory and group them using directory name as base name.

    Args:
        directory (str): Directory path to search

    Returns:
        dict: Dictionary where keys are base names and values are lists of file paths
    """
    mp3_files = []

    # Pattern to match MP3 files with numbers at end: "filename - 01.mp3", "filename - 02.mp3", etc.
    # or at beginning: "01 - filename.mp3", "02 - filename.mp3", "01. filename.mp3", etc.
    pattern_end = re.compile(r"^.+?\s*-\s*(\d+)\.mp3$", re.IGNORECASE)
    pattern_begin = re.compile(r"^(\d+)[\s\.]*[-\s]+.+?\.mp3$", re.IGNORECASE)

    for file in os.listdir(directory):
        if file.lower().endswith(".mp3"):
            # Check if file has a number (either at beginning or end)
            if pattern_end.match(file) or pattern_begin.match(file):
                full_path = os.path.join(directory, file)
                mp3_files.append(full_path)

    # Use directory name as base name if we have multiple numbered files
    if len(mp3_files) > 1:
        base_name = os.path.basename(directory)
        return {base_name: mp3_files}
    else:
        return {}


def sort_mp3_files(file_list):
    """
    Sort MP3 files by their numeric suffix.

    Args:
        file_list (list): List of file paths

    Returns:
        list: Sorted list of file paths
    """

    def extract_number(file_path):
        filename = os.path.basename(file_path)
        # Try number at end first
        match = re.search(r"-\s*(\d+)\.mp3$", filename, re.IGNORECASE)
        if match:
            return int(match.group(1))
        # Try number at beginning (both dash and period formats)
        match = re.search(r"^(\d+)[\s\.]*[-\s]", filename, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 0

    return sorted(file_list, key=extract_number)


def concatenate_mp3s(file_list, output_path):
    """
    Concatenate MP3 files using ffmpeg.

    Args:
        file_list (list): List of MP3 file paths to concatenate
        output_path (str): Path for the output file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create temporary file list for ffmpeg
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as temp_file:
            for file_path in file_list:
                # Escape single quotes for ffmpeg
                escaped_path = file_path.replace("'", "'\\''")
                temp_file.write(f"file '{escaped_path}'\n")
            temp_file_path = temp_file.name

        # Run ffmpeg command
        cmd = [
            "ffmpeg",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            temp_file_path,
            "-c",
            "copy",
            output_path,
            "-y",  # Overwrite output file if it exists
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        # Clean up temp file
        os.unlink(temp_file_path)

        if result.returncode == 0:
            return True
        else:
            print(f"Error running ffmpeg: {result.stderr}")
            return False

    except Exception as e:
        print(f"Error concatenating files: {e}")
        return False


def process_directory(directory):
    """
    Process a single directory, concatenating MP3 groups found within.

    Args:
        directory (str): Directory path to process
    """
    print(f"Processing directory: {directory}")

    mp3_groups = find_mp3_groups(directory)

    if not mp3_groups:
        print(f"  No MP3 groups found in {directory}")
        return

    for base_name, file_list in mp3_groups.items():
        print(f"  Found {len(file_list)} files for '{base_name}'")

        # Sort files by number
        sorted_files = sort_mp3_files(file_list)

        # Create output filename
        output_filename = f"{base_name}.mp3"
        output_path = os.path.join(directory, output_filename)

        # Skip if output file already exists
        if os.path.exists(output_path):
            print(f"    Output file '{output_filename}' already exists, skipping...")
            continue

        print(
            f"    Concatenating {len(sorted_files)} files into '{output_filename}'..."
        )

        # Concatenate files
        if concatenate_mp3s(sorted_files, output_path):
            print(f"    Successfully created '{output_filename}'")
        else:
            print(f"    Failed to create '{output_filename}'")


def main():
    """
    Main function to traverse directories and process MP3 files.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Concatenate MP3 files with the same base name in directories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/audiobooks
  %(prog)s "~/Downloads/Audio Files"
  %(prog)s .  # Process current directory

The script will recursively traverse all subdirectories and concatenate
MP3 files with the same base name (ignoring numbers) into single files.
        """,
    )

    parser.add_argument(
        "directory", nargs="?", help="Target directory to process (required)"
    )

    parser.add_argument("--version", action="version", version="%(prog)s 1.0")

    # Parse arguments
    args = parser.parse_args()

    # Check if directory argument is provided
    if not args.directory:
        warnings.warn(
            "No target directory specified. Please provide a directory path as an argument.",
            UserWarning,
            stacklevel=2,
        )
        print("Usage: python combine_mp3.py <directory>")
        print("Example: python combine_mp3.py /path/to/audiobooks")
        print("Use --help for more information.")
        sys.exit(1)

    # Validate and resolve directory path
    target_dir = os.path.abspath(os.path.expanduser(args.directory))

    if not os.path.exists(target_dir):
        print(f"Error: Directory '{target_dir}' does not exist.")
        sys.exit(1)

    if not os.path.isdir(target_dir):
        print(f"Error: '{target_dir}' is not a directory.")
        sys.exit(1)

    # Check if ffmpeg is available
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: ffmpeg is not installed or not in PATH")
        print("Please install ffmpeg to use this script")
        sys.exit(1)

    print(f"Starting MP3 concatenation from: {target_dir}")

    # Walk through all subdirectories
    for root, dirs, files in os.walk(target_dir):
        # Skip the target directory itself
        if root == target_dir:
            continue

        # Only process directories that contain MP3 files
        if any(file.lower().endswith(".mp3") for file in files):
            process_directory(root)

    print("MP3 concatenation complete!")


if __name__ == "__main__":
    main()
