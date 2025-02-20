from utils import transcribe, process_vtt, parse_subtitle, segment
from spacy.lang.en import English  # Import the English language model
from spacy.lang.zh import Chinese  # Import the Chinese language model
from lmt import rewrite_text  # Importing the module containing rewrite_text
import os
import spacy
import whisper
import gradio as gr
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def process_input(file_path, language):  # Modified function signature
    # Inline determine file type based on extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    audio_exts = {".mp3", ".wav", ".flac", ".aac", ".ogg", "webm", ".m4a"}
    if ext in audio_exts:
        # Use language parameter if provided, otherwise default to None
        lang = language if language.strip() else None
        vtt_file = transcribe(file_path, language=lang)
    else:
        vtt_file = file_path

    # First, rewrite the text
    rewritten = rewrite_text(vtt_file)
    # Then, process the VTT into Markdown and CSV files
    markdown_output, markdown_file_path, csv_file_path, base_name = process_vtt(
        vtt_file
    )
    return rewritten, markdown_file_path, csv_file_path, base_name


def create_interface():
    iface = gr.Interface(
        fn=process_input,
        inputs=[
            gr.File(label="Upload File", type="filepath"),
            gr.Textbox(
                label="Transcribe Language (optional)",
                value="",
                placeholder="e.g., Chinese, English",
            ),
        ],
        outputs=[
            gr.Textbox(label="Final Rewritten Output"),
            gr.File(label="Download Markdown", type="filepath"),
            gr.File(label="Download CSV", type="filepath"),
            gr.Textbox(label="Filename (without extension)"),
        ],
        title="Subtitle/Audio Converter with Rewriting",
        description="Uploads an audio or subtitle file, converts it, rewrites the text, and offers markdown/CSV downloads.",
    )
    return iface


if __name__ == "__main__":
    iface = create_interface()
    iface.launch()

