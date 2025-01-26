import marimo

__generated_with = "0.10.9"
app = marimo.App(width="medium")


@app.cell
def _():
    return


@app.cell
def _():
    import re

    # Example text with repeated Chinese, English words, and punctuation
    text = "好，我看得见，我先先录一下。好好，那。Okay，老板教授我，我先简单的介绍一下你还有我们这个讲座哈可以吗？好好。哎，可以可以可以。现在的这个观众朋友，大家晚上好，现在应该是北京时间晚上八点那么我们这里是光从东方来去介绍东方教会传统的那么中国啊，未处于这个地理的东方所以我们的讲座呢？也涵盖中国教会的历史，那么介绍了中国的教会发展的情况，长达上千年的时间那么今天，我的导师又一次我有线邀请到导师叶青来介绍的情况那么我导师是亚非学院的教授还是他研究的是清代的学术和基督教，还有玛玛语的满文的学习都很厉害，对中亚地区也非常了解，因为它是这个这个总编辑所以感谢大家来参加我们这次学术，性，的，讲座，"

    # Regex pattern to match repeated words/phrases including English, Chinese, and punctuation
    pattern = r"(([\u4e00-\u9fa5A-Za-z，。！？；：“”（）【】《》、]{1,5}))(\s?\1)+"

    # Remove repeated words or phrases by replacing them with a single occurrence
    result = re.sub(pattern, r"\1", text)

    print(result)  

    return pattern, re, result, text


@app.cell
def _():
    import spacy

    # Load Chinese language model
    nlp = spacy.load("zh_core_web_sm")

    def remove_repeated_phrases(text):
        """
        Remove repeated Chinese words and phrases from the input text.
        """
        doc = nlp(text)
        seen_phrases = set()
        result = []

        for token in doc:
            if token.text in seen_phrases:
                continue
            seen_phrases.add(token.text)
            result.append(token.text)

        return "".join(result)

    # Example usage
    text1 = "好，我看得见，我先先录一下。好好，那。Okay，老板教授我，我先简单的介绍一下你还有我们这个讲座哈可以吗？好好。哎，可以可以可以。现在的这个观众朋友，大家晚上好，现在应该是北京时间晚上八点那么我们这里是光从东方来去介绍东方教会传统的那么中国啊，未处于这个地理的东方所以我们的讲座呢？也涵盖中国教会的历史，那么介绍了中国的教会发展的情况，长达上千年的时间那么今天，我的导师又一次我有线邀请到导师叶青来介绍的情况那么我导师是亚非学院的教授还是他研究的是清代的学术和基督教，还有玛玛语的满文的学习都很厉害，对中亚地区也非常了解，因为它是这个这个总编辑所以感谢大家来参加我们这次学术，性，的，讲座，"
    result1 = remove_repeated_phrases(text1)
    print("Original:", text1)
    print("Processed:", result1)
    return nlp, remove_repeated_phrases, result1, spacy, text1


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
