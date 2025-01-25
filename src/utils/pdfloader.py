from langchain_community.document_loaders import PyMuPDFLoader, UnstructuredWordDocumentLoader

mapping = {
    "pdf": PyMuPDFLoader,
    "docx": UnstructuredWordDocumentLoader
}

def loadDocument(filepath: str):
    file_extension = filepath.split('.')[-1].lower()
    if file_extension in mapping:
        LoaderClass = mapping[file_extension]
        loader = LoaderClass(filepath)
        docs = loader.load()
        return docs
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")