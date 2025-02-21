#!/usr/bin/env python3
import argparse
import os
from main import process_input
import dspy

def main():
    parser = argparse.ArgumentParser(
        description="shenbi: Convert audio or subtitle files to CSV and Markdown outputs."
    )
    parser.add_argument("input_file", help="Path to the input audio or subtitle file")
    parser.add_argument("--language", default="", help="Transcribe Language (optional)")
    parser.add_argument("--llm", default="", help="Large Language Model identifier (optional)")
    args = parser.parse_args()

    # Patch dspy.LM.__init__ similarly
    default_model = args.llm.strip() if args.llm.strip() else "ollama/qwen2.5"
    orig_init = dspy.LM.__init__
    def new_init(self, *a, **kw):
        kw["model"] = str(default_model)
        orig_init(self, *a, **kw)
    dspy.LM.__init__ = new_init

    result = process_input(args.input_file, args.language, args.llm)
    print("Markdown Output:", result[0])
    print("Markdown File:", result[1])
    print("CSV File:", result[2])
    print("Filename (without extension):", result[3] if result[3] is not None else "")

if __name__ == "__main__":
    main()