import marimo

__generated_with = "0.10.7"
app = marimo.App(width="full")


@app.cell
def _():
    import gradio as gr
    import marimo as mo
    import os
    import re
    import pandas as pd
    import dspy
    return dspy, gr, mo, os, pd, re


@app.cell
def _(pd, re):
    def parse_subtitle(file_path):
        """Parses various subtitle formats (.srt, .txt, .vtt) into a DataFrame."""
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
def _(dspy, os, parse_subtitle):
    os.environ['GEMINI_API_KEY'] = "GEMINI_API_KEY"
    lm = dspy.LM('gemini/gemini-1.5-flash')
    dspy.configure(lm=lm)

    # Define the signature for the module
    signature = 'text: str -> segmented_text: str'

    # Create the Predict module with the specified signature
    segmenter = dspy.Predict(signature)

    # Define the prompt template for paragraph segmentation
    def segment_text(text):
        prompt = (
            # "Segment the following text into coherent paragraphs. Ensure that each paragraph focuses on a specific topic or idea. Rewrite each paragraph with the same language, with a formal, written style, ensuring the same meaning is preserved:\n\n"
           # "按写作规范重写每个段落，确保保留相同的意思。按文意分段，确保每段有明确主体:\n\n"
           "按文意分段，确保每段有明确主体。删掉口语以及重复性的词句:\n\n"
            f"{text}\n\n"
            "Segmented Text:"
        )
        return segmenter(text=prompt).segmented_text

    file_path = "../../Documents/person/Ware11-20240110.cc.vtt" #This path needs to be valid for your system.

    input_text = "".join(parse_subtitle(file_path)["Content"])

    segmented_output = segment_text(input_text)

    print("重写文字:\n", segmented_output)
    return (
        file_path,
        input_text,
        lm,
        segment_text,
        segmented_output,
        segmenter,
        signature,
    )


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
