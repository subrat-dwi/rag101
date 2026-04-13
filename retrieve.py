from langchain_qdrant import QdrantVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from groq import Groq

# Initialize the Groq client and set up the embedding and vector store
client = Groq()
chat_model = "llama-3.1-8b-instant"
embeddings_model = "all-MiniLM-L6-v2"

embeddings = HuggingFaceEmbeddings(
    model_name=embeddings_model,
)
vector_store = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    url= "http://localhost:6333",
    collection_name= "rag-learning"
)

# Function to retrieve relevant documents based on the query
def retrieve(query: str, vector_store: QdrantVectorStore, top_k=5):
    # embed the query using the same HuggingFaceEmbeddings model
    query_vec = embeddings.embed_query(query)

    # retrieve the most relevant chunks from the vector store
    docs = vector_store.similarity_search_by_vector(query_vec, k=top_k)
    return docs

# Function to generate a response based on the retrieved documents and the query
def generate_response(query: str, vector_store: QdrantVectorStore = vector_store, top_k=5):
    # retrieve relevant documents
    docs = retrieve(query, vector_store, top_k)

    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
Based on the given context, answer the question.
Context: {context}
Question: {query}
"""

    # generate a response using LLM
    response = client.chat.completions.create(
        model=chat_model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided documents."},
            {"role": "user", "content": prompt}
        ]
    )
    return response