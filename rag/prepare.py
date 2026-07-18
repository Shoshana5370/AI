import os
from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

from netfree_unstrict_ssl import unstrict_ssl
unstrict_ssl()

from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone

from structured_data import build_structured_data

# Build structured data from markdown docs
build_structured_data(root_dir="kiro", output_path="structured_data.json")

# Loading
reader = SimpleDirectoryReader(input_dir="kiro")
documents = reader.load_data()
print(f"Loaded documents: {len(documents)}")

# Chunking
node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=20)
nodes = node_parser.get_nodes_from_documents(documents=documents, show_progress=True)
print(f"Generated nodes: {len(nodes)}")

# Embedding
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
embed_model = CohereEmbedding(
    api_key=COHERE_API_KEY,
    model_name="embed-english-v3.0",
    input_type="search_document",
)

# Indexing and Saving
PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
pc = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pc.Index("kiro")
pinecone_vector_store = PineconeVectorStore(pinecone_index=pinecone_index, namespace="kiro-shoshana")

storage_context = StorageContext.from_defaults(vector_store=pinecone_vector_store)
index = VectorStoreIndex.from_documents(
    nodes,
    storage_context=storage_context,
    embed_model=embed_model
)
