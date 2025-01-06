import marimo

__generated_with = "0.10.9"
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
def _(dspy, os):
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
            #"Segment the following text into coherent paragraphs. Ensure that each paragraph focuses on a specific topic or idea:\n\n"
           # "按写作规范重写每个段落，确保保留相同的意思。按文意分段，确保每段有明确主体:\n\n"
           # "按文意分段，确保每段有明确主体:\n\n"
           "删除其中的语气词，比如好，好的等，删除其中重复出现的字词:\n\n"
            f"{text}\n\n"
            "Segmented Text:"
        )
        return segmenter(text=prompt).segmented_text

    input_text = "好，我看得见，我先先录一下。好好，那。Okay，老板教授我，我先简单的介绍一下你还有我们这个讲座哈可以吗？好好。哎，可以可以可以。现在的这个观众朋友，大家晚上好，现在应该是北京时间晚上八点那么我们这里是光从东方来去介绍东方教会传统的那么中国啊，未处于这个地理的东方所以我们的讲座呢？也涵盖中国教会的历史，那么介绍了中国的教会发展的情况，长达上千年的时间那么今天，我的导师又一次我有线邀请到导师叶青来介绍的情况那么我导师是亚非学院的教授还是他研究的是清代的学术和基督教，还有玛玛语的满文的学习都很厉害，对中亚地区也非常了解，因为它是这个这个总编辑所以感谢大家来参加我们这次学术，性，的，讲座，那么接下来的，时间我把时间交给导师朗曼教授老师如果你觉得有一些。中文说不在内。通话我，我，我可以提醒一下就好了，其实都不用做好好好好心，盡心，謝謝謝謝好非常哪些，而且也歡迎你們，就是談我們的那個講座講座的題目。是盧德宗，或還有一個字，就是那個信一叫我，然後給你們介紹。就是特殊的那個意義啊。我，因爲我在倫敦大學是歷史系的一個教師，教授，我先前跟那個路德宗的歷史北京開始講我希望就是不會講得太神但是如果有就是更多，問題，的話那你們可以就是以後就是在問我好，那我題，目就是那個路得住在中國，基本上就是從很本次講座的那個，就是目的。好，那我，我，我不是神學家，但是我，我我看過敏感就是呃，從頭開始。那個宗教改革最重要的地方是什麼？我在坐扁知識防疫下"

    segmented_output = segment_text(input_text)

    print("重写文字:\n", segmented_output)
    return (
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
