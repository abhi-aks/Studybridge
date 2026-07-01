# StudyBridge - TH Bingen AI Assistant

StudyBridge lets you ask questions about TH Bingen, Visa process and nearby dormitory options. It supports english as well as German and can get answers pulled directly from the official university documents (which acts as knowledge base)

Live app: https://huggingface.co/spaces/abhiaks100/studybridge-thb

##What it does
You type a question. The app searches through TH Bingen's official PDFs, pulls the most relevant sections, and hands them to an LLM to generate an answer. It also remembers the last few messages, so follow-up questions work the way you'd expect.

##The documents it knows about:

Module handbook for MSc Computer Science (programs, ECTS credits)
Enrollment and examination regulations
Dormitory prices and room types
Student visa and immigration guide
TH Bingen general fact sheet and ERASMUS information
Full course list with credit hours
(the official document are updated in 2025 so some answers gives older dates)

##How it works
The core idea is RAG (Retrieval Augmented Generation). Instead of relying on what an LLM already knows (which doesn't include TH Bingen's specific dormitory prices), you give it the right documents at query time.

##The pipeline has two phases:
Ingestion (runs once)

PDFs are read page by page using pdfplumber, which handles German characters properly. Pages are split into overlapping chunks of about 1000 characters. Each chunk gets embedded using intfloat/multilingual-e5-small and stored in ChromaDB on disk.

Query (every user question)
The question gets embedded with the same model and compared against all stored chunks. The 8 most relevant and diverse chunks are retrieved using MMR search. Those chunks plus the conversation history go into a prompt, and Groq's LLaMA 3.3 70B generates the final answer.

your question
     |
     v
embed with multilingual-e5-small
     |
     v
search ChromaDB (8912 chunks from TH Bingen PDFs)
     |
     v
top 8 chunks + last 3 conversation turns
     |
     v
LLaMA 3.3 70B via Groq API
     |
     v
streamed answer

##Technologies used
pdfplumber over pypdf: pypdf garbled German characters into question marks. pdfplumber handles them correctly and also extracts tables properly, which was important for the dormitory pricing PDF.

multilingual-e5-small: Students can ask in English but the documents are in German. This model maps both languages into the same vector space, so an English question can match a German chunk. One catch: it requires a "query:" prefix on questions and "passage:" prefix on stored text. Without those prefixes, evaluation scores dropped from 79% to under 10%.

MMR retrieval: Plain similarity search kept returning the same page eight times. MMR (Maximal Marginal Relevance) fetches 20 candidates and picks 8 that are relevant but not redundant.

Groq over OpenAI: Originally planned to use OpenAI but hit quota issues despite having credits. Switched to Groq which is free and runs LLaMA models on custom hardware. Fast enough for streaming.

HuggingFace Spaces with Docker over Streamlit Cloud: Streamlit Cloud defaulted to Python 3.14 which broke sentence-transformers and chromadb. Docker lets you specify Python 3.11 explicitly, which solved it. HuggingFace gives 16GB RAM on the free tier while Render gave about 512MB.

##Evaluation
Testing the system two ways.

Manual keyword matching (24 questions)
Wrote test cases covering dormitory rents, ERASMUS codes, tuition fees, visa document lists, module credits. Checked whether the expected keywords appeared in the answers.
Result: 19 out of 24 passed (79%)

RAGAS automated evaluation (10 questions)

Used RAGAS with Groq as the judge LLM.

Faithfulness: 0.554 (how much of the answer is actually supported by the retrieved chunks)

Answer Relevancy could not be computed because Groq restricts responses to n=1 per call and RAGAS needs n>1 to measure this metric.

##How to run: 
You need to have atleast Python 3.11 and a Groq API key which can be obtained for free using official source. 

git clone https://github.com/abhi-aks/Studybridge.git
cd Studybridge
pip install -r requirements.txt
Add a .env file:

GROQ_API_KEY=your_key_here

Start the app:
streamlit run app.py
The chroma_db folder is already in the repo (stored via Git LFS), so you don't need to run ingestion unless you add new PDFs.

##Project structure
studybridge/
├── app.py                 Streamlit UI, streaming, conversation memory
├── rag.py                 RAG chain, embeddings, retrieval, LLM
├── ingest.py              One-time ingestion pipeline
├── chroma_db/             Pre-built vector database (Git LFS)
├── evaluate1.py           24 manual test cases
├── evaluate2.py           10 additional test cases
├── evaluate_ragas.py      RAGAS automated evaluation
├── Dockerfile             Python 3.11 container for HuggingFace
└── requirements.txt

##Limitations
The Groq free tier has a 100k token daily limit, so heavy usage will hit rate limits. The retry logic in rag.py handles temporary spikes but sustained load will eventually fail.

Faithfulness at 0.554 means the LLM occasionally adds things not in the retrieved chunks. A stronger judge model or better chunking strategy would help here.

Very vague follow-up questions (like "what about the second one?") sometimes fail at the retrieval step because ChromaDB searches on the raw question text, not the interpreted meaning.
