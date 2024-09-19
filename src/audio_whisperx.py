import re
import os
import whisperx
from docx import Document
import gradio as gr

# Initialize the WhisperX model for CPU
model = whisperx.load_model("large-v2", device="cpu", compute_type='int8')  # Use device="cpu" for CPU usage

# Load the diarization model with a Hugging Face token
HUGGING_FACE_TOKEN = "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"  # Replace with your Hugging Face API token
diarization_model = whisperx.DiarizationPipeline(use_auth_token=HUGGING_FACE_TOKEN, device="cpu" )

# Function to transcribe audio to SRT using WhisperX with diarization
def transcribe_audio_with_diarization(file_path):
    # Transcribe using WhisperX with diarization
    result = model.transcribe(file_path)
    
    # Perform speaker diarization
    diarization_result = diarization_model(file_path)
    result = whisperx.align(result, diarization_result)
    
    # Save transcription to SRT format with speaker labels
    srt_file = "transcription_with_speakers.srt"
    with open(srt_file, "w", encoding="utf-8") as f:
        for segment in result['segments']:
            start = whisperx.utils.format_timestamp(segment['start'])
            end = whisperx.utils.format_timestamp(segment['end'])
            speaker = segment['speaker']
            f.write(f"{segment['id']}\n{start} --> {end}\n{speaker}: {segment['text']}\n\n")
    
    return srt_file

# Function to remove timestamps and format text
def remove_timestamps(subtitle_text, file_extension):
    if file_extension == ".srt":
        # Regex to match SRT timestamps like '00:00:01,000 --> 00:00:04,000'
        pattern = r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}'
    elif file_extension == ".cc.vtt" or file_extension == ".vtt":
        # Regex to match VTT timestamps like '00:00:05.000 --> 00:00:10.000'
        pattern = r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}'
    else:
        return subtitle_text  # No cleaning if format is unknown
    
    # Remove timestamps
    cleaned_text = re.sub(pattern, '', subtitle_text)
    
    # Join lines into paragraphs (by removing unnecessary line breaks)
    cleaned_text = re.sub(r'\n{2,}', '\n', cleaned_text)  # Remove extra newlines
    cleaned_text = ' '.join(cleaned_text.splitlines())  # Join remaining lines into a single paragraph
    
    return cleaned_text

# Function to generate DOCX file
def generate_docx(text, filename="cleaned_subtitles.docx"):
    doc = Document()
    doc.add_paragraph(text)
    doc.save(filename)
    return filename

# Function to process files and generate different output formats
def process_files(files):
    subtitles = []
    for file_path in files:
        file_name = os.path.basename(file_path)
        file_extension = os.path.splitext(file_name)[1].lower()

        # If file is audio (mp3, m4a), transcribe it with diarization
        if file_extension in [".mp3", ".m4a"]:
            srt_file = transcribe_audio_with_diarization(file_path)
            with open(srt_file, "r", encoding="utf-8") as f:
                subtitle_text = f.read()
            os.remove(srt_file)
            file_extension = ".srt"  # Treat this as an SRT file
        else:
            # Read subtitle file content
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    subtitle_text = f.read()  # Try UTF-8 first
            except UnicodeDecodeError:
                with open(file_path, "r", encoding="ISO-8859-1") as f:
                    subtitle_text = f.read()  # Fallback to ISO-8859-1 (Latin-1)
        
        # Clean the subtitles by removing timestamps and joining lines
        cleaned_text = remove_timestamps(subtitle_text, file_extension)
        subtitles.append((file_name, cleaned_text.strip()))

    # Create outputs for different formats
    markdown_output = ""
    docx_output = "cleaned_subtitles.docx"
    txt_output = "cleaned_subtitles.txt"

    for filename, cleaned_text in subtitles:
        # Markdown format
        markdown_output += f"# {filename}\n\n"
        markdown_output += cleaned_text + "\n\n"

    # Save Markdown
    with open("cleaned_subtitles.md", "w", encoding="utf-8") as f:
        f.write(markdown_output)
    
    # Save TXT
    with open(txt_output, "w", encoding="utf-8") as f:
        f.write(markdown_output)
    
    # Save DOCX
    generate_docx(markdown_output, docx_output)

    return "cleaned_subtitles.md", docx_output, txt_output

# Gradio Interface
def create_interface():
    with gr.Blocks() as demo:
        # Upload component for subtitle and audio files
        subtitle_input = gr.File(label="Upload .srt, .vtt, .mp3, .m4a files", file_count="multiple", type="filepath", file_types=[".srt", ".vtt", ".cc.vtt", ".mp3", ".m4a"])
        
        # Output components for different formats
        md_output = gr.File(label="Download Cleaned Markdown")
        docx_output = gr.File(label="Download Cleaned DOCX")
        txt_output = gr.File(label="Download Cleaned TXT")

        # Button to process the files
        submit_button = gr.Button("Process Files")
        
        # Process button action and return downloadable files
        submit_button.click(fn=process_files, inputs=subtitle_input, outputs=[md_output, docx_output, txt_output])
    
    return demo

# Run Gradio app
if __name__ == "__main__":
    app = create_interface()
    app.launch()
