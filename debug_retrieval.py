import warnings
warnings.filterwarnings('ignore')
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

embeddings = HuggingFaceEmbeddings(
    model_name='intfloat/multilingual-e5-small',
    encode_kwargs={"normalize_embeddings": True},
)
vectorstore = Chroma(
    collection_name='th_bingen',
    embedding_function=embeddings,
    persist_directory='./chroma_db',
)

questions = [
    ("December deadline", "What is the application deadline for summer term exchange students?"),
    ("B1 German", "What is the minimum language level required for German programs?"),
    ("Inter 2 rent", "What is the rent for an Inter 2 apartment?"),
    ("Childcare leave", "How long can a student take leave of absence for childcare?"),
    ("Mathematics language", "In which language is the Mathematics 1 module taught?"),
]

for label, q in questions:
    print(f"=== {label} ===")
    results = vectorstore.similarity_search("query: " + q, k=5)
    for r in results:
        src = r.metadata['source']
        page = r.metadata['page']
        content = r.page_content.replace('passage: ', '')[:200]
        print(f"  [{src} p{page}] {content}")
        print()
