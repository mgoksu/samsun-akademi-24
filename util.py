
from PyPDF2 import PdfReader

def read_pdf_content(docs, joiner="\n"):
    all_content = ""
    for pdf_doc in docs:
        pdf = PdfReader(pdf_doc)
        all_content += joiner.join([page_obj.extract_text() for page_obj in pdf.pages])
    return all_content
