def count_tokens(markdown_path):
    """
    Calculate the number of tokens in a markdown file.
    Tries to use tiktoken (GPT-2 encoding); if not available, uses jieba for Chinese or whitespace splitting for others.
    """
    try:
        import tiktoken
        encoding = tiktoken.get_encoding("gpt2")
        use_tokenizer = True
    except ImportError:
        use_tokenizer = False

    with open(markdown_path, "r", encoding="utf-8") as f:
        text = f.read()

    if use_tokenizer:
        tokens = encoding.encode(text)
    else:
        # If text contains Chinese, try to use jieba
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            try:
                import jieba
                tokens = jieba.lcut(text)
            except ImportError:
                tokens = list(text)  # fallback: count individual characters
        else:
            tokens = text.split()  # fallback: split by whitespace
    return len(tokens)


def count_csv_tokens(csv_path):
    """
    Calculate the number of tokens in a CSV file.
    Uses the same strategy as count_tokens.
    """
    try:
        import tiktoken
        encoding = tiktoken.get_encoding("gpt2")
        use_tokenizer = True
    except ImportError:
        use_tokenizer = False

    with open(csv_path, "r", encoding="utf-8") as f:
        text = f.read()

    if use_tokenizer:
        tokens = encoding.encode(text)
    else:
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            try:
                import jieba
                tokens = jieba.lcut(text)
            except ImportError:
                tokens = list(text)
        else:
            tokens = text.split()
    return len(tokens)


if __name__ == "__main__":
    import sys, os
    if len(sys.argv) < 2:
        print("Usage: python token.py <file>")
    else:
        file_path = sys.argv[1]
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".csv":
            print("CSV token count:", count_csv_tokens(file_path))
        elif ext in [".md", ".txt", ".json"]:
            print("Markdown/Text/JSON token count:", count_tokens(file_path))
        else:
            print("Unsupported file type. Please provide a markdown (.md), text (.txt), JSON (.json) or CSV (.csv) file.")
