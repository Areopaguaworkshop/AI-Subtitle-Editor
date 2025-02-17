# AI subtitle Editor

The final goal of this project is turn the subtitle into a readable written file by using AI, that is Large Language Model (LLM). 

Launguages are essecial tools for communicate thoughts and ideas, therefore a single words changes will influence the under meaning thoughts which can't be done by AI and should not be. 

This is my personal project for [GCDFL](https://www.gcdfl.org/). The lectures will generate the cc.vtt or srt files. However, I want to make these files into readable markdown file for Chinese audience. 

### you can try the [demo](https://archive.gcdfl.org/), beware, it is in a rapid development, expect changes and errors. 

## Features

- :white_check_mark: Remove transcript timestamps and joining the lines. 

- delete repeated words, phrase and sentences. [Done]

- more. 

## Install

### prerequest
- install [rye](https://rye.astral.sh/)
- [whisper.cpp](https://github.com/ggerganov/whisper.cpp) (optional)
- [whisper](https://github.com/openai/whisper) (optional)

### first step clone this repository

`
git clone https://github.com/Areopaguaworkshop/AI-Subtitle-Editor.git
` 

### second step 

```
cd AI-Subtitle-Editor

mv pyproject.toml pyproject-bk.toml

rye init 

```

### third step

`
copy whole content of the pyproject-bk.toml into pyproject.toml
` 

Then run 

`rye sync`

### four step

`python main.py`

- Then you can access the from http://localhost:7860. 

Enjoy! 

## Roadmap
- to be continue. 

## Workflow
- to be continue. 

### Buy me a Cofee. 

## License:
AI-Subtitle-Editor is licensed under the Apache License 2.0 found in the [LICENSE](https://github.com/Areopaguaworkshop/AI-Subtitle-Editor/blob/main/license.md) file in the root directory of this repository.

## Citation:
```@article{areopagus/AI-Subtitle-Editor,
  title = {AI-Subtitle-Editor},
  author = {Yuan, Yongjia},
  year = {2024},
}

```

