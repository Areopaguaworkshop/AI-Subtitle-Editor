import re
import os
import whisper
from docx import Document
import gradio as gr

# Initialize the Whisper model (this can take time if the model isn't downloaded)
model = whisper.load_model("large-v3")

# Function to transcribe audio to SRT using Whisper with the selected language
def transcribe_audio(file_path, language):
    # Transcribe using Whisper with selected language
    result = model.transcribe(file_path, language=language, fp16=False)
    
    # Save transcription to SRT format
    srt_file = "transcription.srt"
    with open(srt_file, "w", encoding="utf-8") as f:
        for segment in result['segments']:
            start = whisper.utils.format_timestamp(segment['start'])
            end = whisper.utils.format_timestamp(segment['end'])
            f.write(f"{segment['id']}\n{start} --> {end}\n{segment['text']}\n\n")
    
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
def process_files(files, language):
    subtitles = []
    for file_path in files:
        file_name = os.path.basename(file_path)
        file_extension = os.path.splitext(file_name)[1].lower()

        # If file is audio (mp3, m4a), transcribe it
        if file_extension in [".mp3", ".m4a"]:
            srt_file = transcribe_audio(file_path, language)
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
        # Language selection
        language_dropdown = gr.Dropdown(label="Select Language", choices=["en", "zh"], value="en", 
                                        info="Choose 'en' for English and 'zh' for Chinese.")
        
        # Upload component for subtitle and audio files
        subtitle_input = gr.File(label="Upload .srt, .vtt, .mp3, .m4a files", file_count="multiple", type="filepath", file_types=[".srt", ".vtt", ".cc.vtt", ".mp3", ".m4a"])
        
        # Output components for different formats
        md_output = gr.File(label="Download Cleaned Markdown")
        docx_output = gr.File(label="Download Cleaned DOCX")
        txt_output = gr.File(label="Download Cleaned TXT")

        # Button to process the files
        submit_button = gr.Button("Process Files")
        
        # Process button action and return downloadable files
        submit_button.click(fn=process_files, inputs=[subtitle_input, language_dropdown], outputs=[md_output, docx_output, txt_output])
    
    return demo

# Run Gradio app
if __name__ == "__main__":
    app = create_interface()
    app.launch()
