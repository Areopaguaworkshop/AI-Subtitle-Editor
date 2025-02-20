import gradio as gr
import spacy
import os
import re
import pandas as pd
import dspy


def rewrite_text(file_path):
    """Rewrites text from oral to written form using LM of all kinds."""
    """
    os.environ["GEMINI_API_KEY"] = "GEMENI_API_KEY"
    lm = dspy.LM("gemini/gemini-1.5-flash")
    # Previous configuration:
    # Commented out HuggingFace configuration:
    lm = dspy.LM(
        model="huggingface/openbmb/MiniCPM-o2_6",
        provider="huggingface",  # Added provider parameter to resolve error
        max_tokens=15000,
        timeout_s=1200,
    #     token=os.environ.get('HF_ACCESS_TOKEN')  # Provide your HuggingFace access token via env variable
    )
    """
    lm = dspy.LM(
        model="ollama/qwen2.5",
        base_url="http://localhost:11434",
        max_tokens=25000,
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
        raise ValueError(
            "Invalid language. Supported languages are 'zh' and 'en'.")

    # Read the text from the file
    from utils import parse_subtitle  # assuming parse_subtitle is defined in utils.py

    vtt_df = parse_subtitle(file_path)
    text = "".join(vtt_df["Content"])
    # with open(file_path, 'r', encoding='utf-8-sig') as f:
    #  text = f.read()

    # Segment the text into 10 sentences
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents][:6]

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
    rewritten = "".join(rewritten_sentences)

    return rewritten
