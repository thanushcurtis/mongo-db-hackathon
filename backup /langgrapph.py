import os
from typing import List, TypedDict
from dotenv import load_dotenv
from langchain_voyageai import VoyageAIEmbeddings
from langchain_cohere import ChatCohere
from langchain_mongodb import MongoDBAtlasVectorSearch
from langgraph.graph import StateGraph, END
from pymongo import MongoClient

# Load environment variables from .env
load_dotenv()

# Define the schema for our graph state
class GraphState(TypedDict):
    question: str
    generation: str
    documents: List[str]

# Initialize Models
embeddings = VoyageAIEmbeddings(
    voyage_api_key=os.getenv("VOYAGE_API_KEY"),
    model="voyage-finance-2"
)

llm = ChatCohere(
    cohere_api_key=os.getenv("COHERE_API_KEY"),
    model="command-r-plus-08-2024"
)

# Initialize MongoDB Atlas Vector Store
mongo_client = MongoClient(os.getenv("MONGO_URI"))
collection = mongo_client["rag_db"]["documents"]

vector_store = MongoDBAtlasVectorSearch(
    collection=collection,
    embedding=embeddings,
    index_name="vector_index",
    text_key="text",
    embedding_key="embedding",
)

def retrieve(state: GraphState):
    print("---RETRIEVING---")
    question = state["question"]
    documents = vector_store.similarity_search(question, k=3)
    return {"documents": documents, "question": question}

def generate(state: GraphState):
    print("---GENERATING---")
    question = state["question"]
    documents = state["documents"]

    # Format prompt
    context = "\n\n".join([doc.page_content for doc in documents])
    prompt = f"Answer the question: {question} \n\n Using only this context: {context}"

    response = llm.invoke(prompt)
    return {"generation": response.content, "question": question}


workflow = StateGraph(GraphState)

# Add Nodes
workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)

# Build Edges
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

# Compile the graph
app = workflow.compile()

print("Graph compiled successfully!")

if __name__ == "__main__":
    # Test question to run through the pipeline
    test_question = "What is MongoDB Atlas?"
    print(f"\nAsking: {test_question}")
    
    # Invoke the graph with the initial state
    inputs = {"question": test_question, "documents": [], "generation": ""}
    result = app.invoke(inputs)
    
    print("\n--- AI RESPONSE ---")
    print(result["generation"])
