import marimo

__generated_with = "0.10.9"
app = marimo.App(width="full")


@app.cell
def _():
    import gradio as gr
    import marimo as mo
    import spacy
    import os
    import re
    import pandas as pd
    return gr, mo, os, pd, re, spacy


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
def _(parse_subtitle, re):
    def rm_rep(file_path):
        """Removes repeated words/phrases from a file."""
        try:
            vtt_df = parse_subtitle(file_path)
            all_content = "".join(vtt_df["Content"])
            pattern = r"(([\u4e00-\u9fa5A-Za-z，。！？；：“”（）【】《》、]{1,5}))(\s?\1)+"
            return re.sub(pattern, r"\1", all_content)
        except Exception as e:
            return f"An error occurred: {e}"
    return (rm_rep,)


@app.cell
def _(os, parse_subtitle, rm_rep):
    def process_vtt(file_path):
        """Processes various subtitle file types and returns markdown, CSV file path, and filename."""
        try:
            base_name, _ = os.path.splitext(file_path)
            csv_file_path = base_name + ".csv"
            markdown_file_path = base_name + ".md"

            # Export to CSV
            vtt_df = parse_subtitle(file_path)
            vtt_df.to_csv(csv_file_path, index=False, encoding='utf-8')
            print(f"CSV file '{csv_file_path}' created successfully.")

            # Create Markdown
            md_content = "".join(vtt_df["Content"])

             # Regex pattern to match repeated words/phrases including English, Chinese, and punctuation
            #pattern = r"(([\u4e00-\u9fa5A-Za-z，。！？；：“”（）【】《》、]{1,5}))(\s?\1)+"
            markdown_output = rm_rep(md_content)

            # nlp = spacy.blank("zh")

            # custom oral word list
            # oral_words={"嗯", "啊", "呃", "嘛"}
            # doc =nlp(rm_repeat)
            # filtered_tokens = [token.rm_repeat for token in doc if token.rm_repeat not in oral_words]

            # markdown_output = "".join(filtered_tokens)

            # Write markdown to file
            with open(markdown_file_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"Markdown file '{markdown_file_path}' created successfully.")

            return markdown_output, markdown_file_path, csv_file_path, base_name

        except Exception as e:
            return f"An error occurred: {e}", None, None, None
    return (process_vtt,)


@app.cell
def _(gr, process_vtt):
    def create_interface():
        iface = gr.Interface(
            fn=process_vtt, # Changed to the new function
            inputs=gr.File(label="Upload VTT Subtitle File", type="filepath"),
            outputs=[
                gr.Textbox(label="Markdown Output"),
                gr.File(label="Download Markdown", type="filepath"),
                gr.File(label="Download CSV", type="filepath"),
                gr.Textbox(label="Filename (without extension)")
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
