import argparse  # added for command line argument parsing
import whisper
import spacy
import os
from utils import transcribe, process_vtt, parse_subtitle, segment 
import re
import subprocess
import pandas as pd
from spacy.lang.zh import Chinese  # Import the Chinese language model
from spacy.lang.en import English  # Import the English language model

def process_input(file_path, language):  # Modified function signature
    # Inline determine file type based on extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    audio_exts = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}
    if ext in audio_exts:
        # Use language parameter if provided, otherwise default to None
        lang = language if language.strip() else None
        vtt_file = transcribe(file_path, language=lang)
        return process_vtt(vtt_file)
    else:
        return process_vtt(file_path)

def main():
    parser = argparse.ArgumentParser(description="Subtitle/Audio Converter")
    parser.add_argument("input_file", help="Path to the input file")
    parser.add_argument("--language", default="", help="Transcribe Language (optional)")
    args = parser.parse_args()

    result = process_input(args.input_file, args.language)
    # Output the processed result; customize as needed
    print(result)

if __name__ == "__main__":
    main()