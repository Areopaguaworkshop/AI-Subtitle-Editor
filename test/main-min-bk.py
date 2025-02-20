import gradio as gr
import os
from utils import transcribe, process_vtt 

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

def create_interface():
    iface = gr.Interface(
        fn=process_input,
        inputs=[
            gr.File(label="Upload File", type="filepath"),
            gr.Textbox(label="Transcribe Language (optional)", value="", placeholder="e.g., Chinese, English")
        ],
        outputs=[
            gr.Textbox(label="Markdown Output"),
            gr.File(label="Download Markdown", type="filepath"),
            gr.File(label="Download CSV", type="filepath"),
            gr.Textbox(label="Filename (without extension)")
        ],
        title="Subtitle/Audio Converter",
        description="Uploads an audio or subtitle file and converts it to Markdown and CSV formats.",
    )
    return iface

if __name__ == "__main__":
    iface = create_interface()
    iface.launch()