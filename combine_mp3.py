#!/usr/bin/env python3
"""
MP3 Concatenation Script

This script traverses directories recursively and combines MP3 files with the same base name
(ignoring numbers) into a single concatenated file using ffmpeg.

Example:
    "Der Aufstieg des Erddrachen - 01.mp3" + "Der Aufstieg des Erddrachen - 02.mp3" + ...
    becomes "Der Aufstieg des Erddrachen.mp3"
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path
from collections import defaultdict


def find_mp3_groups(directory):
    """
    Find MP3 files in a directory and group them by base name.

    Args:
        directory (str): Directory path to search

    Returns:
        dict: Dictionary where keys are base names and values are lists of file paths
    """
    mp3_groups = defaultdict(list)

    # Pattern to match MP3 files with numbers: "basename - 01.mp3", "basename - 02.mp3", etc.
    pattern = re.compile(r'^(.+?)\s*-\s*(\d+)\.mp3$', re.IGNORECASE)

    for file in os.listdir(directory):
        if file.lower().endswith('.mp3'):
            match = pattern.match(file)
            if match:
                base_name = match.group(1).strip()
                full_path = os.path.join(directory, file)
                mp3_groups[base_name].append(full_path)

    # Only return groups with multiple files
    return {k: v for k, v in mp3_groups.items() if len(v) > 1}


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
        match = re.search(r'-\s*(\d+)\.mp3$', filename, re.IGNORECASE)
        return int(match.group(1)) if match else 0

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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            for file_path in file_list:
                # Escape single quotes for ffmpeg
                escaped_path = file_path.replace("'", "'\\''")
                temp_file.write(f"file '{escaped_path}'\n")
            temp_file_path = temp_file.name

        # Run ffmpeg command
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', temp_file_path,
            '-c', 'copy',
            output_path,
            '-y'  # Overwrite output file if it exists
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
            print(f"    Output file '{
                  output_filename}' already exists, skipping...")
            continue

        print(f"    Concatenating {len(sorted_files)
                                   } files into '{output_filename}'...")

        # Concatenate files
        if concatenate_mp3s(sorted_files, output_path):
            print(f"    Successfully created '{output_filename}'")
        else:
            print(f"    Failed to create '{output_filename}'")


def main():
    """
    Main function to traverse directories and process MP3 files.
    """
    # Check if ffmpeg is available
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: ffmpeg is not installed or not in PATH")
        print("Please install ffmpeg to use this script")
        return

    current_dir = os.getcwd()
    print(f"Starting MP3 concatenation from: {current_dir}")

    # Walk through all subdirectories
    for root, dirs, files in os.walk(current_dir):
        # Skip the current directory itself
        if root == current_dir:
            continue

        # Only process directories that contain MP3 files
        if any(file.lower().endswith('.mp3') for file in files):
            process_directory(root)

    print("MP3 concatenation complete!")


if __name__ == "__main__":
    main()
