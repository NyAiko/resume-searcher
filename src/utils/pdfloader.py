import pymupdf

def extractText(filepath:str):
  pdf = pymupdf.open(filepath)
  extracted_text= ""
  for page in pdf.pages():
    text = page.get_text()
    text = text.strip()
    text = text.replace("\n", " ")
    extracted_text += "\n" + text
  return text
