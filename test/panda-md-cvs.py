import marimo

__generated_with = "0.10.7"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import os
    import pandas as pd
    return mo, os, pd


@app.cell
def _(pd):
    def parse_vtt(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        timestamps = []
        contents = []
        current_content = []

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if "-->" in line:
                timestamps.append(line)
                i += 1  # Move to the next line (content)
                current_content = []
                while i < len(lines) and lines[i].strip() and not lines[i].strip().isdigit():
                    current_content.append(lines[i].strip())
                    i += 1
                contents.append(" ".join(current_content))
            else:
                i += 1 #Skip lines that are not timestamps

        return pd.DataFrame({"Timestamps": timestamps, "Content": contents})

    file_path = "../../Documents/person/Ware11-20240110.cc.vtt" #This path needs to be valid for your system.
    vtt_df = parse_vtt(file_path)
    print(vtt_df.head())
    return file_path, parse_vtt, vtt_df


@app.cell
def _(file_path, os, vtt_df):
    # Extract the base name from the file path.
    base_name, _ = os.path.splitext(file_path)

    # Construct the CSV file path.
    csv_file_path = base_name + ".csv"

    try:
        # Export the DataFrame to a CSV file.
        vtt_df.to_csv(csv_file_path, index=False, encoding='utf-8')  # index=False prevents writing row indices
        print(f"CSV file '{csv_file_path}' created successfully.")
    except Exception as e:
        print(f"An error occurred while creating the CSV file: {e}")

    #Optional: Verify the file was created.
    if os.path.exists(csv_file_path):
        print(f"File '{csv_file_path}' created successfully.")
    else:
        print(f"File '{csv_file_path}' was not created.")
    return base_name, csv_file_path


@app.cell
def _(base_name, os, vtt_df):
    # Extract the 'Content' column and join the lines.
    all_content = "".join(vtt_df["Content"])

    # Create a markdown file.
    markdown_file_path = base_name +".md"
    with open(markdown_file_path, "w", encoding="utf-8") as f:
        f.write(all_content)

    print(f"Markdown file '{markdown_file_path}' created successfully.")

    #Optional: Verify the file was created.
    if os.path.exists(markdown_file_path):
        print(f"File '{markdown_file_path}' created successfully.")
    else:
        print(f"File '{markdown_file_path}' was not created.")
    return all_content, f, markdown_file_path


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
