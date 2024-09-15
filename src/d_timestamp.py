import os
import re
import gradio as gr
from haystack import Pipeline

# Define a node to remove timestamps for both .srt and .vtt formats
class TimestampRemover:
    def run(self, subtitle_text, file_extension):
        if file_extension == ".srt":
            # Regex to match SRT timestamps like '00:00:01,000 --> 00:00:04,000'
            pattern = r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}'
        elif file_extension == ".cc.vtt":
            # Regex to match VTT timestamps like '00:00:05.000 --> 00:00:10.000'
            pattern = r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}'
        else:
            return {"text": subtitle_text}, "output_1"  # No cleaning if format is unknown
        
        # Remove timestamps
        cleaned_text = re.sub(pattern, '', subtitle_text)
        return {"text": cleaned_text}, "output_1"

# Step 3: Process files and generate markdown output
def process_subtitles(files):
    # Initialize the Haystack pipeline
    remover_node = TimestampRemover()
    pipeline = Pipeline()
    pipeline.add_node(component=remover_node, name="TimestampRemover", inputs=["FileReader"])
    
    subtitles = []
    
    # Process each uploaded file
    for file in files:
        file_extension = ".srt" if file.name.endswith(".srt") else ".cc.vtt"
        content = file.read().decode('utf-8')
        
        # Clean the subtitles
        result = pipeline.run(content, file_extension=file_extension)
        cleaned_text = result['text']
        
        # Append filename and cleaned text for markdown generation
        subtitles.append((file.name, cleaned_text.strip()))
    
    # Generate markdown output
    markdown_output = ""
    for filename, cleaned_text in subtitles:
        markdown_output += f"# {filename}\n\n"
        markdown_output += cleaned_text + "\n\n"
    
    return markdown_output

# Gradio Interface
interface = gr.Interface(
    fn=process_subtitles,                 # Function to process files
    inputs=gr.File(file_count="multiple", type="filepath", file_types=[".srt", ".vtt"]),  # Upload input
    outputs=gr.Markdown(),                # Output markdown result
    title="Subtitle Timestamp Remover",   # Title of the interface
    description="Upload .srt or .cc.vtt files to remove timestamps and get cleaned text in markdown."
)

# Launch Gradio app
if __name__ == "__main__":
    interface.launch()
