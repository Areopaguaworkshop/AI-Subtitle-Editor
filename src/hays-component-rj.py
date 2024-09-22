import re
from haystack import Pipeline
from haystack.nodes import FileTypeClassifier, LocalWhisperTranscriber, BaseComponent
from haystack.utils import clean_wav_audio_file
import gradio as gr
import os
from docx import Document


# Custom node to remove timestamps and join lines
class RemoveTimestampsJoinLines(BaseComponent):
    def run(self, file_paths, file_extension):
        cleaned_texts = []
        for path in file_paths:
            # Remove timestamps based on file extension
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Select pattern based on file type
            if file_extension == ".srt":
                pattern = r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}'
            elif file_extension in [".vtt", ".cc.vtt"]:
                pattern = r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}'
            else:
                pattern = ""
            
            # Remove timestamps and join lines
            if pattern:
                content = re.sub(pattern, '', content)
                content = re.sub(r'\d+\n', '', content)  # Remove line numbers in SRT
                content = re.sub(r'\n{2,}', ' ', content)  # Remove extra newlines
                content = re.sub(r'\n', ' ', content).strip()  # Join lines
            
            cleaned_texts.append(content)

        return {"cleaned_texts": cleaned_texts}

    def run_batch(self, *args, **kwargs):
        raise NotImplementedError("run_batch not implemented for RemoveTimestampsJoinLines")

# Custom node to convert text to DOCX, Markdown, and TXT
class ConvertToOutputFiles(BaseComponent):
    def run(self, cleaned_texts):
        docx_filename = "cleaned_text.docx"
        markdown_filename = "cleaned_text.md"
        txt_filename = "cleaned_text.txt"
        
        # Create DOCX
        doc = Document()
        for text in cleaned_texts:
            doc.add_paragraph(text)
        doc.save(docx_filename)
        
        # Create Markdown
        with open(markdown_filename, 'w', encoding='utf-8') as md_file:
            for text in cleaned_texts:
                md_file.write(text + "\n\n")
        
        # Create TXT
        with open(txt_filename, 'w', encoding='utf-8') as txt_file:
            for text in cleaned_texts:
                txt_file.write(text + "\n\n")
        
        return {"docx_output": docx_filename, "markdown_output": markdown_filename, "txt_output": txt_filename}

    def run_batch(self, *args, **kwargs):
        raise NotImplementedError("run_batch not implemented for ConvertToOutputFiles")

# Create the Haystack pipeline
def create_haystack_pipeline():
    pipeline = Pipeline()

    # Add a FileTypeClassifier node to differentiate between audio and subtitle files
    file_classifier = FileTypeClassifier(
        pdf=None,
        txt=None,
        docx=None,
        html=None,
        json=None,
        csv=None,
        audio=[".mp3", ".m4a"],
        subtitle=[".srt", ".vtt", ".cc.vtt"]
    )

    # Add LocalWhisperTranscriber node for audio transcription
    transcriber = LocalWhisperTranscriber(model_name_or_path="large-v2")

    # Add custom nodes for cleaning and formatting text
    remove_timestamps_node = RemoveTimestampsJoinLines()
    convert_to_output_node = ConvertToOutputFiles()

    # Add nodes to the pipeline
    pipeline.add_node(component=file_classifier, name="FileClassifier", inputs=["File"])
    pipeline.add_node(component=transcriber, name="Transcriber", inputs=["FileClassifier.audio"])
    pipeline.add_node(component=remove_timestamps_node, name="RemoveTimestampsJoinLines", inputs=["FileClassifier.subtitle", "Transcriber"])
    pipeline.add_node(component=convert_to_output_node, name="ConvertToOutputFiles", inputs=["RemoveTimestampsJoinLines"])

    return pipeline

# Function to process files and return outputs
def process_files_with_pipeline(file_paths):
    pipeline = create_haystack_pipeline()

    # Preprocess file paths
    files = [{"file_path": path} for path in file_paths]

    # Run the pipeline
    results = pipeline.run_batch(files=files)

    return results["markdown_output"], results["docx_output"], results["txt_output"]

# Gradio Interface
def create_gradio_interface():
    with gr.Blocks() as demo:
        # Upload component for subtitle and audio files
        file_input = gr.File(label="Upload .srt, .vtt, .mp3, .m4a files", file_count="multiple", type="filepath", file_types=[".srt", ".vtt", ".cc.vtt", ".mp3", ".m4a"])
        
        # Output components for different formats
        md_output = gr.File(label="Download Cleaned Markdown")
        docx_output = gr.File(label="Download Cleaned DOCX")
        txt_output = gr.File(label="Download Cleaned TXT")

        # Button to process the files
        submit_button = gr.Button("Process Files")
        
        # Process button action and return downloadable files
        submit_button.click(fn=process_files_with_pipeline, inputs=file_input, outputs=[md_output, docx_output, txt_output])
    
    return demo

# Run Gradio app
if __name__ == "__main__":
    app = create_gradio_interface()
    app.launch()
