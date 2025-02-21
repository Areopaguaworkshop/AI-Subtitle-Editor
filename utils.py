import os
import whisper
import spacy
import re
import pandas as pd
from spacy.lang.zh import Chinese  # Import the Chinese language model
from spacy.lang.en import English  # Import the English language model
from moviepy.audio.io.AudioFileClip import AudioFileClip  # Use AudioFileClip for audio conversion

def parse_subtitle(file_path):
    """Parses various subtitle formats (.ass, .sub, .srt, .txt, .vtt) into a DataFrame."""
    try:
        with open(file_path, 'r', encoding='utf-8-sig', errors='replace') as file:
            lines = file.readlines()
    except FileNotFoundError:
        return pd.DataFrame(columns=["Timestamps", "Content"])
    except ImportError:
        print("pysrt library not found. Falling back to less robust parsing.")

    timestamps = []
    contents = []
    current_content = []

    if file_path.lower().endswith(".txt"):
        contents = lines
        timestamps = [''] * len(contents)
    else:
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            #Improved .sub handling:
            if "-->" in line or re.match(r'\d{2}:\d{2}:\d{2},\d{2} --> \d{2}:\d{2}:\d{2},\d{2}', line):
                timestamps.append(line)
                i += 1
                current_content = []
                while i < len(lines) and lines[i].strip() and not re.match(r'\d{2}:\d{2}:\d{2},\d{2} --> \d{2}:\d{2}:\d{2},\d{2}', lines[i].strip()):
                    current_content.append(lines[i].strip())
                    i += 1
                contents.append(" ".join(current_content))
            elif "Dialogue:" in line or re.match(r'{\d+}{\d+}.*', line):
                timestamps.append(line)
                i += 1
                current_content = []
                while i < len(lines) and lines[i].strip() and not lines[i].strip().isdigit():
                    current_content.append(lines[i].strip())
                    i += 1
                contents.append(" ".join(current_content))
            else:
                i += 1

    return pd.DataFrame({"Timestamps": timestamps, "Content": contents})

def rm_rep(file_path):
    """Removes repeated words/phrases from a file."""
    try:
        vtt_df = parse_subtitle(file_path)
        all_content = "".join(vtt_df["Content"])
        pattern = r"(([\u4e00-\u9fa5A-Za-z，。！？；：“”（）【】《》、]{1,5}))(\s?\1)+"
        return re.sub(pattern, r"\1", all_content)
    except Exception as e:
        return f"An error occurred: {e}"

def transcribe(file_path, language=None):
    """
    Transcribes an audio file (assumed to be in WAV format) to a WebVTT file.
    """
    base, ext = os.path.splitext(file_path)
    ext = ext.lower()
    # Removed audio conversion: assuming file_path is already a WAV file.
    model = whisper.load_model("large-v3-turbo", device="cpu")
    # Use a specified language if provided, otherwise use auto-detection
    if language:
        result = model.transcribe(file_path, fp16=False, verbose=True, language=language)
    else:
        result = model.transcribe(file_path, fp16=False, verbose=True)
    text = result.get("text", "").strip()

    vtt_content = "WEBVTT\n\n00:00:00.000 --> 00:00:10.000\n" + text
    out_file = os.path.abspath(base + ".vtt")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(vtt_content)
    
    return out_file

def segment(file_path):
    """
    Segments a text file into paragraphs by grouping every 12 sentences.
    Identifies the language (Chinese or English) and returns the paragraphs joined with double newlines.
    """
    text = rm_rep(file_path) 

    # Detect language
    if any(char in text for char in '，。？！'):
        nlp = Chinese()
    else:
        nlp = English()

    # Add the sentencizer component to the pipeline
    nlp.add_pipe("sentencizer")
    doc = nlp(text)

    paragraphs = []
    current_paragraph = []
    sentence_count = 0
    for sent in doc.sents:
        current_paragraph.append(sent.text)
        sentence_count += 1
        if sentence_count >= 8:
            paragraphs.append(''.join(current_paragraph))
            current_paragraph = []
            sentence_count = 0

    if current_paragraph:
        paragraphs.append(''.join(current_paragraph))

    segmented_text = '\n\n'.join(paragraphs)
    return segmented_text

def rewrite_text(file_path):
    """Rewrites text by first segmenting the file into paragraphs,
    then rewriting each paragraph one at a time."""
    import dspy
    import spacy
    # Use the segment function to segment the text into paragraphs
    segmented_text = segment(file_path)
    # Assume paragraphs are separated by double newlines
    paragraphs = segmented_text.split("\n\n")
    
    # Set up the language and spacy model
    language = "en"
    if language == "zh":
        nlp = spacy.load("zh_core_web_sm")
    elif language == "en":
        nlp = spacy.load("en_core_web_sm")
    else:
        raise ValueError("Invalid language. Supported languages are 'zh' and 'en'.")
    
    # Configure the LM WITHOUT hard-coding 'model'
    lm = dspy.LM(
        base_url="http://localhost:11434",
        max_tokens=50000,
        timeout_s=3600,
        temperature=0.2
    )
    dspy.configure(lm=lm)
    
    rewritten_paragraphs = []
    # Loop over paragraphs and rewrite each one individually
    for para in paragraphs:
        class ParaRewrite(dspy.Signature):
            """
            重写此段，将口语表达变成书面表达，确保意思不变。
            保证重写后的文本长度不少于原文的95%。
            """
            text: str = dspy.InputField(desc="需要重写的口语讲座")
            rewritten: str = dspy.OutputField(desc="重写后的段落")
        
        rewrite = dspy.ChainOfThought(ParaRewrite)
        response = rewrite(text=para)
        rewritten_paragraphs.append(response.rewritten)
    
    rewritten_text = "\n\n".join(rewritten_paragraphs)
    return rewritten_text

def process_vtt(file_path):
    """Processes various subtitle file types and returns markdown, CSV file path, and filename."""
    try:
        _, filename = os.path.split(file_path)
        base_name, _ = os.path.splitext(filename)
        csv_file_path = base_name + ".csv"
        markdown_file_path = base_name + ".md"

        # Export to CSV
        vtt_df = parse_subtitle(file_path)
        vtt_df.to_csv(csv_file_path, index=False, encoding='utf-8')
        print(f"CSV file '{csv_file_path}' created successfully.")

        # Create Markdown
        markdown_output = rewrite_text(file_path)

        # Write markdown to file
        with open(markdown_file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_output)
        print(f"Markdown file '{markdown_file_path}' created successfully.")

        return markdown_output, markdown_file_path, csv_file_path, base_name
    except Exception as e:
        return f"An error occurred: {e}", None, None, None
