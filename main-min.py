import gradio as gr
import whisper
import spacy
import os
from utils import transcribe, process_vtt, parse_subtitle, segment 
import re
import subprocess
import pandas as pd
from spacy.lang.zh import Chinese  # Import the Chinese language model
from spacy.lang.en import English  # Import the English language model
import shutil  # add import if not already imported

def process_input(file_path):
    # Copy file from temporary location to persistent directory
    uploads_dir = "/home/ajiap/project/Sub-Ed/uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    filename = os.path.basename(file_path)
    persistent_path = os.path.join(uploads_dir, filename)
    shutil.copy(file_path, persistent_path)
    
    # Inline check for audio file based on extension using persistent_path
    _, ext = os.path.splitext(persistent_path)
    ext = ext.lower()
    audio_ext = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}
    if ext in audio_ext:
        vtt_file = transcribe(persistent_path)
        return process_vtt(vtt_file)
    else:
        return process_vtt(persistent_path)

def create_interface():
    iface = gr.Interface(
        fn=process_input,  # Changed from process_vtt to process_input
        inputs=gr.File(label="Upload File", type="filepath"),
        outputs=[
            gr.Textbox(label="Markdown Output"),
            gr.File(label="Download Markdown", type="filepath"),
            gr.File(label="Download CSV", type="filepath"),
            gr.Textbox(label="Filename (without extension)")
        ],
        title="Lecturer written-text Converter",
        description="Uploads an audio or subtitle file and converts it to Markdown and CSV formats.",
    )
    return iface

if __name__ == "__main__":
    iface = create_interface()
    iface.launch()