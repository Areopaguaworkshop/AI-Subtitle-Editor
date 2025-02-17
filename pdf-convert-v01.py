# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "marker==2.1.5",
#     "ocrmypdf==16.8.0",
#     "pillow==10.4.0",
# ]
# ///

import marimo

__generated_with = "0.10.15"
app = marimo.App(width="medium")


@app.cell
def _():
    import ocrmypdf
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered
    import os

    def process_pdf(file_path):
        # Generate the OCR-processed PDF file name
        base_name = os.path.splitext(file_path)[0]
        ocr_pdf_path = f"{base_name}-ocr.pdf"

        # Perform OCR on the PDF
        ocrmypdf.ocr(
            file_path, ocr_pdf_path, language="chi_sim+chi_tra", force_ocr=True
        )

        # Convert the OCR-processed PDF to Markdown
        converter_config = {
            "force_ocr": False,
            "extract_images": False,
            "extract_tables": True,
            "extract_figures": False,
            "extract_equations": True,
            "extract_code": True,
            "extract_references": True,
        }

        converter = PdfConverter(artifact_dict=create_model_dict(), **converter_config)
        rendered = converter(ocr_pdf_path)
        text, _, _ = text_from_rendered(rendered)

        # Save the Markdown output
        md_file_path = f"{base_name}.md"
        with open(md_file_path, "w", encoding="utf-8") as md_file:
            md_file.write(text)

        print(f"OCR-processed PDF saved as: {ocr_pdf_path}")
        print(f"Markdown file saved as: {md_file_path}")

    # Example usage
    if __name__ == "__main__":
        # Replace with your PDF file path
        input_pdf = "/home/ajiap/Documents/pdf-md-data/Xu-Tiesheng-2014-中华姓氏源流大辞典 (徐铁生编著).pdf"
        process_pdf(input_pdf)
    return (
        PdfConverter,
        create_model_dict,
        input_pdf,
        ocrmypdf,
        os,
        process_pdf,
        text_from_rendered,
    )


if __name__ == "__main__":
    app.run()
