import os
import whisper
import spacy
import re
import subprocess
import pandas as pd
from spacy.lang.zh import Chinese  # Import the Chinese language model
from spacy.lang.en import English  # Import the English language model

def parse_subtitle(file_path):
    """Parses various subtitle formats (.ass, .sub, .srt, .txt, .vtt) into a DataFrame."""
    try:
        #subtitles = pysrt.open(file_path)
        #timestamps = [str(sub.start).replace('.', ',') + " --> " + str(sub.end).replace('.', ',') for sub in subtitles]
        #contents = [sub.text for sub in subtitles]
        #return pd.DataFrame({"Timestamps": timestamps, "Content": contents})
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

def segment(file_path):
    """
    Segments a text file into paragraphs based on meaning,
    identifying the language (Chinese or English) and joining
    the paragraphs with newline characters.
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

    # Segment into paragraphs based on meaning
    paragraphs = []
    current_paragraph = []
    sentence_count = 0
    for sent in doc.sents:
        if sentence_count == 0:
            current_paragraph.append(sent.text)
            sentence_count += 1
        else:
            # Check if the sentence's meaning is similar to the previous one
            similarity = sent.similarity(doc[len(current_paragraph) - 1])
            if similarity > 0.5 or sentence_count < 15:  # Adjust threshold as needed
                current_paragraph.append(sent.text)
                sentence_count += 1
            else:
                paragraphs.append(''.join(current_paragraph))
                current_paragraph = [sent.text]
                sentence_count = 1

    # Add the last paragraph
    if current_paragraph:
        paragraphs.append(''.join(current_paragraph))

    # Join paragraphs with newlines
    segmented_text = '\n\n'.join(paragraphs)
    return segmented_text

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
        markdown_output = segment(file_path)

        # Write markdown to file
        with open(markdown_file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_output)
        print(f"Markdown file '{markdown_file_path}' created successfully.")

        return markdown_output, markdown_file_path, csv_file_path, base_name
    except Exception as e:
        return f"An error occurred: {e}", None, None, None

def transcribe(file_path):
    """
    Transcribes an MP3 or M4A audio file to a WebVTT file using CPU.
    """
    base, _ = os.path.splitext(file_path)
    # Removed m4a conversion step, assuming the model supports it directly
    model = whisper.load_model("large-v3-turbo", device="cpu")
    result = model.transcribe(file_path, fp16=False, verbose=True)
    text = result.get("text", "").strip()

    # Create simple VTT output. For production, cue timings should be generated dynamically.
    vtt_content = "WEBVTT\n\n00:00:00.000 --> 00:00:10.000\n" + text

    out_file = base + ".vtt"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(vtt_content)
    
    return out_file
