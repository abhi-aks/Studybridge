import os
import re
from pathlib import Path
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
import pdfplumber

load_dotenv()

PDFS_DIR = "pdfs"
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "th_bingen"
EMBED_MODEL = "intfloat/multilingual-e5-small"

# PDFs that are primarily tables — extract tables instead of plain text
TABLE_PDFS = {"Prices and Amenities of Dormitories.pdf", "THB-ALL-COURSES-ECTS.pdf"}


def extract_table_as_text(page, source, page_num):
    """Convert table rows into readable sentences."""
    docs = []
    tables = page.extract_tables()
    for table in tables:
        for row in table:
            # Clean None values and join non-empty cells
            cells = [str(c).strip() for c in row if c and str(c).strip()]
            if len(cells) >= 2:
                text = " | ".join(cells)
                text = re.sub(r'\s+', ' ', text).strip()
                if len(text) > 30:
                    docs.append(Document(
                        page_content="passage: " + text,
                        metadata={"source": source, "page": page_num}
                    ))
    return docs


def load_pdfs(folder):
    documents = []
    for pdf_path in sorted(Path(folder).glob("*.pdf")):
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_num = i + 1
                    source = pdf_path.name

                    if source in TABLE_PDFS:
                        # Use table extraction for table-heavy PDFs
                        docs = extract_table_as_text(page, source, page_num)
                        documents.extend(docs)
                    else:
                        # Use plain text extraction for regular PDFs
                        text = page.extract_text() or ""
                        text = re.sub(r'\s+', ' ', text).strip()
                        if len(text) > 100:
                            documents.append(Document(
                                page_content="passage: " + text,
                                metadata={"source": source, "page": page_num}
                            ))
        except Exception as e:
            print(f"  [WARN] Could not read {pdf_path.name}: {e}")
    return documents


def main():
    print("Loading PDFs...")
    documents = load_pdfs(PDFS_DIR)
    print(f"Loaded {len(documents)} chunks from {len(set(d.metadata['source'] for d in documents))} PDFs")

    # Table PDFs are already chunked row by row — only split regular text docs
    table_docs = [d for d in documents if d.metadata['source'] in TABLE_PDFS]
    text_docs = [d for d in documents if d.metadata['source'] not in TABLE_PDFS]

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=400)
    split_docs = splitter.split_documents(text_docs)

    all_chunks = split_docs + table_docs
    print(f"Total chunks after splitting: {len(all_chunks)}")

    print("Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )

    print("Embedding and storing in ChromaDB...")
    Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DIR,
    )
    print(f"Done. {len(all_chunks)} chunks stored in {CHROMA_DIR}/")


if __name__ == "__main__":
    main()
