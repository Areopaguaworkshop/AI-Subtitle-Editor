import os
import whisper
import re
from docx import Document
import gradio as gr

# Initialize the Whisper model
model = whisper.load_model("large-v2")

# Function to transcribe audio directly to text without timestamps
def transcribe_audio_to_text(file_path):
    result = model.transcribe(file_path, fp16=False)
    # Concatenate all segments to get plain text
    plain_text = " ".join([segment['text'] for segment in result['segments']])
    return plain_text.strip()

# Function to remove timestamps and join lines for subtitle files
def remove_timestamps_and_join_lines(subtitle_text, file_extension):
    if file_extension == ".srt":
        pattern = r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}'
    elif file_extension in [".cc.vtt", ".vtt"]:
        pattern = r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}'
    else:
        return subtitle_text

    # Remove timestamps
    cleaned_text = re.sub(pattern, '', subtitle_text)
    # Remove line numbers (in SRT files) and extra newlines
    cleaned_text = re.sub(r'^\d+\n', '', cleaned_text, flags=re.MULTILINE)
    cleaned_text = re.sub(r'\n{2,}', ' ', cleaned_text)  # Join paragraphs
    # Join remaining lines
    cleaned_text = re.sub(r'\n', ' ', cleaned_text).strip()  
    
    return cleaned_text

# Function to generate DOCX file
def generate_docx(text, filename="cleaned_text.docx"):
    doc = Document()
    doc.add_paragraph(text)
    doc.save(filename)
    return filename

# Main function to handle input files and generate outputs
def process_files(file_paths):
    all_texts = []
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        file_extension = os.path.splitext(file_name)[1].lower()

        # Step 1: If audio file, transcribe to plain text
        if file_extension in [".mp3", ".m4a"]:
            plain_text = transcribe_audio_to_text(file_path)
            cleaned_text = plain_text  # Audio transcription doesn't need further cleaning
        # Step 2: If it's a subtitle file, clean it
        elif file_extension in [".srt", ".vtt", ".cc.vtt"]:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    subtitle_text = f.read()
            except UnicodeDecodeError:
                with open(file_path, "r", encoding="ISO-8859-1") as f:
                    subtitle_text = f.read()
            
            # Clean the subtitles by removing timestamps and joining lines
            cleaned_text = remove_timestamps_and_join_lines(subtitle_text, file_extension)
        else:
            continue  # Skip unsupported file types

        all_texts.append((file_name, cleaned_text.strip()))

    # Create outputs for different formats
    markdown_output = ""
    docx_output = "cleaned_text.docx"
    txt_output = "cleaned_text.txt"

    for filename, cleaned_text in all_texts:
        # Markdown format
        markdown_output += f"# {filename}\n\n"
        markdown_output += cleaned_text + "\n\n"

    # Save Markdown
    with open("cleaned_text.md", "w", encoding="utf-8") as f:
        f.write(markdown_output)
    
    # Save TXT
    with open(txt_output, "w", encoding="utf-8") as f:
        f.write(markdown_output)
    
    # Save DOCX
    generate_docx(markdown_output, docx_output)

    return "cleaned_text.md", docx_output, txt_output

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
