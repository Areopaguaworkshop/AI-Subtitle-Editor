from utils import transcribe, process_vtt
import os
import gradio as gr
import sys
import dspy

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def process_input(file_path, language, llm):  # Modified function signature
    # Patch dspy.LM.__init__ so that its "model" parameter is always a string.
    default_model = llm.strip() if llm.strip() else "ollama/qwen2.5"
    orig_init = dspy.LM.__init__
    def new_init(self, *args, **kw):
        kw["model"] = str(default_model)
        orig_init(self, *args, **kw)
    dspy.LM.__init__ = new_init

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

    # Get result from process_vtt and ensure result has exactly 4 values
    result = process_vtt(vtt_file)
    # Slice to first 4 items in case more are returned
    return result[:4]


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
            gr.Textbox(
                label="LLM Model (optional)",
                value="ollama/qwen2.5",
                placeholder="Enter LLM model identifier"
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

