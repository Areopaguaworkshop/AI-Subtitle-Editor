# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "dspy==2.5.43",
#     "g==0.0.7",
#     "google-generativeai==0.8.4",
#     "gradio==5.12.0",
#     "marimo",
#     "pandas==2.2.3",
#     "pip==24.3.1",
#     "spacy==3.8.4",
# ]
# ///

import marimo

__generated_with = "0.10.15"
app = marimo.App(width="full")


@app.cell
def _():
    import gradio as gr
    import marimo as mo
    import spacy
    import os
    import re
    import pandas as pd
    import dspy
    import spacy

    return dspy, gr, mo, os, pd, re, spacy


@app.cell
def _(pd, re):
    def parse_subtitle(file_path):
        """Parses various subtitle formats (.ass, .sub, .srt, .txt, .vtt) into a DataFrame."""
        try:
            with open(file_path, "r", encoding="utf-8-sig") as file:
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
            timestamps = [""] * len(contents)
        else:
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                # Improved .sub handling:
                if "-->" in line or re.match(
                    r"\d{2}:\d{2}:\d{2},\d{2} --> \d{2}:\d{2}:\d{2},\d{2}", line
                ):  # Check for common .sub timestamp format
                    timestamps.append(line)
                    i += 1
                    current_content = []
                    while (
                        i < len(lines)
                        and lines[i].strip()
                        and not re.match(
                            r"\d{2}:\d{2}:\d{2},\d{2} --> \d{2}:\d{2}:\d{2},\d{2}",
                            lines[i].strip(),
                        )
                    ):  # Check for next timestamp
                        current_content.append(lines[i].strip())
                        i += 1
                    contents.append(" ".join(current_content))
                elif "Dialogue:" in line or re.match(
                    r"{\d+}{\d+}.*", line
                ):  # Handles .ass
                    timestamps.append(line)
                    i += 1
                    current_content = []
                    while (
                        i < len(lines)
                        and lines[i].strip()
                        and not lines[i].strip().isdigit()
                    ):
                        current_content.append(lines[i].strip())
                        i += 1
                    contents.append(" ".join(current_content))
                else:
                    i += 1

        return pd.DataFrame({"Timestamps": timestamps, "Content": contents})

    return (parse_subtitle,)


@app.cell
def _(dspy, parse_subtitle, spacy):
    def rewrite_text(file_path):
        """Rewrites text from oral to written form using LM of all kinds."""
        """
        os.environ["GEMINI_API_KEY"] = "GEMENI_API_KEY"
        lm = dspy.LM("gemini/gemini-1.5-flash")
        """
        # lm=dspy.LM(model='ollama/deepseek-r1:8b', base_url= "http://localhost:11434", max_tokens= 1000, timeout_s=600)
        lm = dspy.LM(
            model="ollama/qwen2.5",
            base_url="http://localhost:11434",
            max_tokens=15000,
            timeout_s=1200,
        )
        dspy.configure(lm=lm)
        language = "en"
        # Load the appropriate spacy model based on the language
        if language == "zh":
            nlp = spacy.load("zh_core_web_sm")
        elif language == "en":
            nlp = spacy.load("en_core_web_sm")
        else:
            raise ValueError("Invalid language. Supported languages are 'zh' and 'en'.")

        # Read the text from the file
        vtt_df = parse_subtitle(file_path)
        text = "".join(vtt_df["Content"])
        # with open(file_path, 'r', encoding='utf-8-sig') as f:
        #  text = f.read()

        # Segment the text into 10 sentences
        doc = nlp(text)
        sentences = [sent.text for sent in doc.sents][:8]

        # Rewrite each sentence using Gemini API
        rewritten_sentences = []
        for sentence in sentences:
            # define signature
            class OraltoWrite(dspy.Signature):
                """重写口语表达为书面语言，确保意思一致，字数相当"""

                sentence: str = dspy.InputField(desc="需要重写口语表达")
                response: str = dspy.OutputField(desc="转换后的书面表达")

            rewrite = dspy.ChainOfThought(OraltoWrite)
            response = rewrite(sentence=sentence)
            rewritten_sentences.append(response.response)

        # Join the rewritten sentences back into a single string
        rewritten = "。".join(rewritten_sentences)

        return rewritten

    return (rewrite_text,)


@app.cell
def _(os, parse_subtitle, rewrite_text):
    def process_vtt(file_path):
        try:
            _, filename = os.path.split(file_path)
            base_name, _ = os.path.splitext(filename)
            csv_file_path = base_name + ".csv"
            markdown_file_path = base_name + ".md"

            # Export to CSV
            vtt_df = parse_subtitle(file_path)
            vtt_df.to_csv(csv_file_path, index=False, encoding="utf-8")
            print(f"CSV file '{csv_file_path}' created successfully.")

            # Create Markdown
            markdown_output = rewrite_text(file_path)

            # Write markdown to file
            with open(markdown_file_path, "w", encoding="utf-8") as f:
                f.write(markdown_output)
            print(f"Markdown file '{markdown_file_path}' created successfully.")

            return markdown_output, markdown_file_path, csv_file_path, base_name

        except Exception as e:
            return f"An error occurred: {e}", None, None, None

    return (process_vtt,)


@app.cell
def _(gr, process_vtt):
    def create_interface():
        iface = gr.Interface(
            fn=process_vtt,  # Changed to the new function
            inputs=gr.File(label="Upload VTT Subtitle File", type="filepath"),
            outputs=[
                gr.Textbox(label="Markdown Output"),
                gr.File(label="Download Markdown", type="filepath"),
                gr.File(label="Download CSV", type="filepath"),
                gr.Textbox(label="Filename (without extension)"),
            ],
            title="subtitle fiel to Markdown/CSV Converter",
            description="Upload a subtitle file (only surpport .vtt, .srt) to convert it to Markdown and CSV formats.",
        )
        return iface

    iface = create_interface()
    iface.launch()
    return create_interface, iface


if __name__ == "__main__":
    app.run()
