import os
import chromadb
from chromadb.utils import embedding_functions

class VectorDBSetup:
    """
    Class to handle the initialization of the ChromaDB vector store and collection.
    """

    def __init__(self, client_manager):
        self.vector_store_path = client_manager.get_vector_store_path()
        self.embedding_model = client_manager.get_embedding_model()
        

    def initialize_vectorDB(self):
        """
        Initializes the ChromaDB client and retrieves or creates a collection.
        """
        try:
            client = chromadb.PersistentClient(path=self.vector_store_path)
            sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=self.embedding_model)

            collection = client.get_or_create_collection(
                name="documents_collection", 
                embedding_function=sentence_transformer_ef
            )
            return collection

        except Exception as e:
            raise RuntimeError(f"Failed to initialize vector database: {e}")

