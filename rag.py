import time
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from groq import RateLimitError

load_dotenv()

CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "th_bingen"
EMBED_MODEL = "intfloat/multilingual-e5-small"

PROMPT_TEMPLATE = """
You are StudyBridge, a helpful assistant for international students at TH Bingen
(Technische Hochschule Bingen), a university of applied sciences in Germany.

Answer the question using only the context below, which comes from official TH Bingen documents.
If the context does not contain the answer, say you don't have that information and suggest
the student contact the International Office at international@th-bingen.de.

- Respond in the same language the user writes in.
- Translate German source text naturally — do not paste raw German unless asked.
- Keep answers concise. Cite the source document for specific numbers or dates.

Context:
{context}

Question:
{question}
"""


def format_docs(docs):
    return "\n\n---\n\n".join(
        f"[{doc.metadata.get('source', 'unknown')}, page {doc.metadata.get('page', '?')}]\n{doc.page_content}"
        for doc in docs
    )


def build_chain():
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 8, "fetch_k": 20},
    )

    def retrieve_with_prefix(question):
        return retriever.invoke("query: " + question)

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

    chain = (
        {"context": RunnableLambda(retrieve_with_prefix) | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


def answer_with_retry(chain, question, max_retries=3):
    """Call chain with retry on rate limit — used by app.py for resilience."""
    for attempt in range(max_retries):
        try:
            return chain.invoke(question)
        except RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(10 * (attempt + 1))
            else:
                raise
