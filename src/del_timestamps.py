import os
import re
import gradio as gr

# Define a function to remove timestamps for both .srt and .vtt formats
def remove_timestamps(subtitle_text, file_extension):
    if file_extension == ".srt":
        # Regex to match SRT timestamps like '00:00:01,000 --> 00:00:04,000'
        pattern = r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}'
    elif file_extension == ".cc.vtt":
        # Regex to match VTT timestamps like '00:00:05.000 --> 00:00:10.000'
        pattern = r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}'
    else:
        return subtitle_text  # No cleaning if format is unknown
    
    # Remove timestamps
    cleaned_text = re.sub(pattern, '', subtitle_text)
    return cleaned_text

# Step 2: Process files and generate markdown output
def process_subtitles(files):
    subtitles = []
    
    # Process each uploaded file
    for file in files:
        file_extension = ".srt" if file.name.endswith(".srt") else ".cc.vtt"
        content = file.decode('utf-8')
        
        # Clean the subtitles by removing timestamps
        cleaned_text = remove_timestamps(content, file_extension)
        
        # Append filename and cleaned text for markdown generation
        subtitles.append((file.name, cleaned_text.strip()))
    
    # Generate markdown output
    markdown_output = ""
    for filename, cleaned_text in subtitles:
        markdown_output += f"# {filename}\n\n"
        markdown_output += cleaned_text + "\n\n"
    
    return markdown_output

# Gradio Interface
def create_interface():
    with gr.Blocks() as demo:
        # Upload component for .srt and .cc.vtt files
        subtitle_input = gr.File(label="Upload .srt or .cc.vtt files", file_count="multiple", type="filepath", file_types=[".srt", ".vtt"])
        
        # Output component for markdown
        markdown_output = gr.Markdown(label="Cleaned Subtitles")

        # Button to process the files
        submit_button = gr.Button("Process Subtitles")
        
        # Process button action
        submit_button.click(fn=process_subtitles, inputs=subtitle_input, outputs=markdown_output)
    
    return demo

# Run Gradio app
if __name__ == "__main__":
    app = create_interface()
    app.launch()
