"""
Phase 2 Evaluation — RAGAS automated evaluation.
Usage: python evaluate_ragas.py
"""

from rag import build_chain
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from ragas import evaluate
from ragas.metrics import _Faithfulness, _ResponseRelevancy
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from datasets import Dataset
import warnings
warnings.filterwarnings('ignore')

CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "th_bingen"
EMBED_MODEL = "intfloat/multilingual-e5-small"

# Questions to evaluate — mix of topics
QUESTIONS = [
    "What is the ERASMUS code for TH Bingen?",
    "What is the tuition fee per semester for incoming exchange students?",
    "What is the application portal for incoming exchange students?",
    "What is the email address of the International Office?",
    "What is the rent for an Inter 2 apartment?",
    "What is the rent for a wheelchair accessible apartment in Inter 2?",
    "What documents are needed for a German student visa?",
    "What is the workload for the Artificial Intelligence module in MSc Computer Science?",
    "How many ECTS is the Artificial Intelligence module worth?",
    "What is the rent for a Weisenau apartment?",
]


def get_contexts(question, vectorstore):
    """Retrieve the actual chunks used for a question."""
    results = vectorstore.similarity_search("query: " + question, k=8)
    return [doc.page_content.replace("passage: ", "") for doc in results]


def main():
    print("Loading RAG chain and vector store...")
    chain = build_chain()

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )

    # Build dataset: question + generated answer + retrieved contexts
    print("Generating answers and retrieving contexts...")
    data = {"question": [], "answer": [], "contexts": []}

    for i, question in enumerate(QUESTIONS, 1):
        print(f"  [{i}/{len(QUESTIONS)}] {question[:60]}...")
        answer = chain.invoke(question)
        contexts = get_contexts(question, vectorstore)
        data["question"].append(question)
        data["answer"].append(answer)
        data["contexts"].append(contexts)

    dataset = Dataset.from_dict(data)

    # RAGAS needs an LLM and embedding model to act as judge
    judge_llm = LangchainLLMWrapper(ChatGroq(model="llama-3.1-8b-instant", temperature=0))
    judge_embeddings = LangchainEmbeddingsWrapper(embeddings)

    print("\nRunning RAGAS evaluation...")
    results = evaluate(
        dataset=dataset,
        metrics=[_Faithfulness(), _ResponseRelevancy()],
        llm=judge_llm,
        embeddings=judge_embeddings,
    )

    print("\n" + "=" * 60)
    print("RAGAS RESULTS")
    print("=" * 60)
    df = results.to_pandas()
    print(f"Faithfulness:     {df['faithfulness'].mean():.3f}  (is answer grounded in context?)")
    try:
        print(f"Answer Relevancy: {df['answer_relevancy'].mean():.3f}  (does answer address the question?)")
    except Exception:
        print("Answer Relevancy: could not compute (Groq n>1 limitation)")
    print("=" * 60)
    print("\nScore guide: 0.0 = terrible | 0.5 = average | 1.0 = perfect")


if __name__ == "__main__":
    main()
