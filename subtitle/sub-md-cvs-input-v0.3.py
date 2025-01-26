# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "google-generativeai==0.8.4",
#     "gradio==5.13.1",
#     "marimo",
#     "pandas==2.2.3",
#     "spacy==3.8.4",
# ]
# ///

import marimo

__generated_with = "0.10.15"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import os
    import re
    import pandas as pd
    import spacy
    from spacy.lang.zh import Chinese  # Import the Chinese language model
    from spacy.lang.en import English  # Import the English language model
    return Chinese, English, mo, os, pd, re, spacy


@app.cell
def _(pd, re):
    def parse_subtitle(file_path):
        """Parses various subtitle formats (.ass, .sub, .srt, .txt, .vtt) into a DataFrame."""
        try:
            #subtitles = pysrt.open(file_path)
            #timestamps = [str(sub.start).replace('.', ',') + " --> " + str(sub.end).replace('.', ',') for sub in subtitles]
            #contents = [sub.text for sub in subtitles]
            #return pd.DataFrame({"Timestamps": timestamps, "Content": contents})

            with open(file_path, 'r', encoding='utf-8-sig') as file:
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
                if "-->" in line or re.match(r'\d{2}:\d{2}:\d{2},\d{2} --> \d{2}:\d{2}:\d{2},\d{2}', line): #Check for common .sub timestamp format
                    timestamps.append(line)
                    i += 1
                    current_content = []
                    while i < len(lines) and lines[i].strip() and not re.match(r'\d{2}:\d{2}:\d{2},\d{2} --> \d{2}:\d{2}:\d{2},\d{2}', lines[i].strip()): #Check for next timestamp
                        current_content.append(lines[i].strip())
                        i += 1
                    contents.append(" ".join(current_content))
                elif "Dialogue:" in line or re.match(r'{\d+}{\d+}.*', line): #Handles .ass
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
    return (parse_subtitle,)


@app.cell
def _(e, parse_subtitle, re):
    def rm_rep(file_path):
        """Removes repeated words/phrases from a file."""
        try:
            vtt_df = parse_subtitle(file_path)
            all_content = "，".join(vtt_df["Content"])
            pattern = r"(([\u4e00-\u9fa5A-Za-z，。！？；：“”（）【】《》、]{1,5}))(\s?\1)+"
            return re.sub(pattern, r"\1", all_content)
        except Exception as error:
            return f"An error occurred: {e}", None
    return (rm_rep,)


@app.cell
def _(Chinese, English, rm_rep):
    def segment(file_path):
        """
        Segments a text file into paragraphs based on meaning,
        identifying the language (Chinese or English) and joining
        the paragraphs with newline characters.

        Args:
        file_path (str): The path to the text file.

        Returns:
        str: The segmented text with paragraphs separated by newlines.
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
                if similarity > 0.4 or sentence_count < 15:  # Adjust threshold as needed
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
        segmented_text = ''.join(paragraphs)

        return segmented_text
    return (segment,)


@app.cell
def _(os, parse_subtitle, segment):
    def process_vtt(file_path):
        """Processes various subtitle file types and returns markdown, CSV file path, and filename."""
        try:
            '''
            base_name, _ = os.path.splitext(file_path)
            csv_file_path = base_name + ".csv"
            markdown_file_path = base_name + ".md"
            '''

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

            # nlp = spacy.blank("zh")

            # custom oral word list
            # oral_words={"嗯", "啊", "呃", "嘛"}
            # doc =nlp(rm_repeat)
            # filtered_tokens = [token.rm_repeat for token in doc if token.rm_repeat not in oral_words]

            # markdown_output = "".join(filtered_tokens)

            # Write markdown to file
            with open(markdown_file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_output)
            print(f"Markdown file '{markdown_file_path}' created successfully.")

            return markdown_output, markdown_file_path, csv_file_path, base_name

        except Exception as e:
            return f"An error occurred: {e}", None, None, None
            return (process_vtt,)
    return (process_vtt,)


@app.cell
def _():
    return


@app.cell
def _(process_vtt):
    # Example usagerro
    file_path = "/home/ajiap/Documents/person/ware11-20250117.vtt"  # Replace with your actual file path
    markdown_output, markdown_file_path, csv_file_path, base_name = process_vtt(file_path)

    print(f"Markdown Output: {markdown_output}")
    print(f"Markdown File Path: {markdown_file_path}")
    print(f"CSV File Path: {csv_file_path}")
    return (
        base_name,
        csv_file_path,
        file_path,
        markdown_file_path,
        markdown_output,
    )


if __name__ == "__main__":
    app.run()
