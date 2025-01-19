import marimo

__generated_with = "0.10.9"
app = marimo.App(width="medium")


@app.cell
def _():
    import nltk
    nltk.download('stopwords')
    return (nltk,)


@app.cell
def _():
    from nltk.corpus import stopwords
    stop_word = stopwords.words('chinese')
    print(stop_word)
    return stop_word, stopwords


@app.cell
def _():
    import gradio as gr
    import marimo as mo
    import os
    import re
    import pandas as pd
    return gr, mo, os, pd, re


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
    return (parse_subtitle,)


@app.cell
def _(parse_subtitle, stopwords, word):
    def rm_oral(file_path): 
    # sample text
        vtt_df = parse_subtitle(file_path)

    # add stopwords
    # add_stopw = {'example','ajia'}
    # stop_words.update(add_stopw)

    # remove stop words
    # stop_words.discard('not')

    # Tokenize the text
        filered_word = [word for word in word.tokenize(vtt_df['Content'].sum()) if word.lower() not in stopwords.words('chinese')]

        return filered_word
        return (rm_oral,)
    return (rm_oral,)


app._unparsable_cell(
    r"""
    import spacy

    # Load Chinese language model
    nlp = spacy.load(\"zh_core_web_sm\")

    def remove_repeated_phrases(file_path):
        \"\"\"
        Remove repeated Chinese words and phrases from the input text.
        \"\"\"
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            text = file.read()
        doc = nlp(text)
        seen_phrases = set()
        result = []

        for token in doc:
            if token.text in seen_phrases:
                continue
            seen_phrases.add(token.text)
            result.append(token.text)
        rm-repeat = \"\".join(result)
        return rm-repeat
        return (remove_repeated_phrases,)
    """,
    name="_"
)


@app.cell
def _(filered_word, repeat, rm):
    if __name__ == "__main__":
        file_path = "/home/ajiap/Documents/person/Ajia-Spirit4-20240525.cc.vtt"
    print (
           file_path,
           filered_word,
           rm-repeat,
       )
    return (file_path,)


if __name__ == "__main__":
    app.run()
