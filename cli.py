#!/usr/bin/env python3
import argparse
import os
from main import process_input

def main():
    parser = argparse.ArgumentParser(
        description="shenbi: Convert audio or subtitle files to CSV and Markdown outputs."
    )
    parser.add_argument("input_file", help="Path to the input audio or subtitle file")
    parser.add_argument("--language", default="", help="Transcribe Language (optional)")
    args = parser.parse_args()

    result = process_input(args.input_file, args.language)
    print("Markdown Output:", result[0])
    print("Markdown File:", result[1])
    print("CSV File:", result[2])
    print("Filename (without extension):", result[3] if result[3] is not None else "")

if __name__ == "__main__":
    main()