# Policy Document Corpus

## Current corpus
The default corpus in `documents.py` uses **synthetic Swiss public health
insurance (KVG / LAMal) clauses** for demonstration purposes.

## Replacing with real documents

1. Place your PDF or plain-text policy documents in this folder.
2. Update `documents.py` (or replace it with a PDF loader):

```python
# Example: load from PDFs using LangChain
from langchain_community.document_loaders import PyPDFDirectoryLoader

loader = PyPDFDirectoryLoader("data/corpus/")
docs = loader.load_and_split()
```

3. Re-index by restarting the server (the FAISS index is built at startup).

## Real public sources for Swiss insurance documents
- **BAG (Bundesamt für Gesundheit)**: https://www.bag.admin.ch/bag/de/home/versicherungen/krankenversicherung.html
- **FINMA**: https://www.finma.ch/en/supervision/insurance/
- KVG/LAMal consolidated legislation: https://www.fedlex.admin.ch/eli/cc/1995/1328_1328_1328/en

## GDPR / data protection note
If you use real customer policy documents, ensure they are anonymised before
indexing. The vector store (FAISS) stores embeddings on disk — treat the
`faiss_index/` folder with the same confidentiality as the source documents.
