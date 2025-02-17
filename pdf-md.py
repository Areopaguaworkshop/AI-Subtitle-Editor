# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "fitz==0.0.1.dev2",
#     "marimo",
#     "marker==2.1.5",
#     "marker-pdf==1.3.4",
#     "ocrmypdf==16.8.0",
#     "pillow==10.4.0",
#     "PyMuPDF==1.18.16",
# ]
# ///

import marimo

__generated_with = "0.10.17"
app = marimo.App()


@app.cell
def _():
    # import ocrmypdf and marker-pdf, pymupdf here
    import ocrmypdf
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered
    import os
    import fitz
    import marimo as mo
    return (
        PdfConverter,
        create_model_dict,
        fitz,
        mo,
        ocrmypdf,
        os,
        text_from_rendered,
    )


@app.cell
def _(PdfConverter, fitz, os):
    # write a function to segements a big pdf into ten segments pdf file
    def split_pdf(file_path, output_dir):
        pdf = fitz.open(file_path)
        total_pages = pdf.page_count
        segment_size = total_pages // 10
        for i in range(10):
            start = i * segment_size
            end = (i + 1) * segment_size
            if i == 9:
                end = total_pages
            segment = fitz.open()
            for j in range(start, end):
                segment.insert_pdf(pdf, from_page=j, to_page=j)
            segment.save(os.path.join(output_dir, f"{i}.pdf"))
            segment.close()
        pdf.close()

    # turn the pdf file in the output_dir into markdown file through marker-pdf, then join these markdown files into one
    def pdf_to_md(file_path, output_dir):
        split_pdf(file_path, output_dir)
        md_files = []
        for i in range(10):
            pdf_file = os.path.join(output_dir, f"{i}.pdf")
            md_file = os.path.join(output_dir, f"{i}.md")
            PdfConverter().convert(pdf_file, md_file)
            md_files.append(md_file)
        with open(os.path.join(output_dir, "output.md"), "w") as f:
            for md_file in md_files:
                with open(md_file, "r") as md:
                    f.write(md.read())

    # set the input pdf file path and output directory here
    pdf_file = "/home/ajiap/Documents/pdf-md-data/Xu-Tiesheng-2014-中华姓氏源流大辞典 (徐铁生编著)-ocr.pdf"
    output_dir = "Xu-Tiesheng-2014-中华姓氏源流大辞典"
    pdf_to_md(pdf_file, output_dir)
    return output_dir, pdf_file, pdf_to_md, split_pdf


if __name__ == "__main__":
    app.run()
