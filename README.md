# LegalAI — Nyaya Mitra

LegalAI is a Streamlit application for exploring Indian legal information and reviewing contract documents. It combines a retrieval-augmented legal chatbot, PDF contract analysis, and Firebase-based account features in one interface.

> **Disclaimer:** LegalAI is an educational project and does not provide legal advice. Always consult a qualified legal professional for decisions involving legal rights or obligations.

## Features

- **Indian law chatbot** — retrieves relevant context from a local FAISS index and generates concise or detailed answers with a Together-hosted language model.
- **Contract analysis** — extracts text from PDF files, summarizes documents, answers questions, identifies potentially unfair or ambiguous clauses, and performs sentiment/emotion analysis.
- **Account management** — supports Firebase email sign-up, sign-in, and password reset.
- **Streamlit interface** — provides a simple sidebar for switching between the chatbot, contract analyzer, and account pages.

## Technology

- Python and Streamlit
- LangChain, Together AI, and FAISS
- Hugging Face Transformers and Sentence Transformers
- spaCy
- Firebase Authentication and Admin SDK
- PyPDF2

## Project structure

```text
LegalAI/
├── main.py                  # Streamlit entry point and navigation
├── appchat.py               # Retrieval-augmented legal chatbot
├── app2.py                  # PDF contract analysis
├── account1.py              # Account page used by main.py
├── account.py               # Alternate account implementation
├── footer.py                # Shared footer component
├── data/ipc_law.txt         # Indian Penal Code source text
├── images/                  # Application images
└── .streamlit/config.toml   # Streamlit theme
```

The following required local resources are intentionally excluded from Git:

- `ipc_embed_db/` — generated FAISS vector index.
- Firebase service-account JSON — private server credential.
- `testing_pdf/` — local test and uploaded documents.

## Prerequisites

- Python 3.10 or 3.11
- A Together AI API key
- A Firebase project with Email/Password authentication enabled
- A Firebase service-account JSON file
- A compatible FAISS index in `ipc_embed_db/`

## Installation

Clone the repository and enter its directory:

```powershell
git clone https://github.com/mohanraokulkarni/LegalAI.git
cd LegalAI
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the application dependencies:

```powershell
python -m pip install --upgrade pip
pip install streamlit streamlit-option-menu langchain langchain-community langchain-together faiss-cpu sentence-transformers transformers torch spacy firebase-admin requests PyPDF2 numpy htbuilder
python -m spacy download en_core_web_sm
```

The first run may take several minutes because the embedding and document-analysis models are downloaded and cached locally.

## Configuration

### 1. API keys

Set the required keys as environment variables:

```powershell
$env:TOGETHER_API_KEY="your-together-api-key"
$env:FIREBASE_API_KEY="your-firebase-web-api-key"
```

Alternatively, create `.streamlit/secrets.toml` locally:

```toml
TOGETHER_API_KEY = "your-together-api-key"
FIREBASE_API_KEY = "your-firebase-web-api-key"
```

`.streamlit/secrets.toml` is ignored by Git and must never be committed.

### 2. Firebase service account

Download a service-account JSON file from the Firebase console and keep it outside version control. Either place it in the project using the expected local filename:

```text
nyaya-mitra-3df4c-22c18cac6e9f.json
```

or point the application to a different location:

```powershell
$env:FIREBASE_CREDENTIALS_PATH="C:\secure\firebase-service-account.json"
```

### 3. FAISS legal index

The chatbot expects a LangChain FAISS index at `ipc_embed_db/`. Build or copy an index generated from `data/ipc_law.txt` with the `law-ai/InLegalBERT` embedding model. The directory must contain the files produced by `FAISS.save_local()`.

The legal chatbot cannot start until this directory is available. The index is excluded from Git because it is generated data and may be large.

## Running the application

From the repository root, run:

```powershell
streamlit run main.py
```

Streamlit will print the local application URL, normally `http://localhost:8501`.

## Security

- Never commit API keys, `.env` files, Streamlit secrets, or Firebase service-account credentials.
- Restrict Firebase and Together API credentials to only the permissions the application needs.
- Treat uploaded contracts as confidential and avoid retaining them longer than necessary.
- Rotate a credential immediately if it is accidentally exposed.

## Known limitations

- Generated answers can be inaccurate or incomplete and must be independently verified.
- Contract analysis currently supports text-based PDF files; scanned PDFs require OCR before upload.
- Model downloads and inference can require substantial memory and processing time.
- The chatbot focuses on the bundled Indian Penal Code source and is not a complete or automatically updated collection of Indian law.

## Author

Mohan Rao — [mohanraokulkarni](https://github.com/mohanraokulkarni)
