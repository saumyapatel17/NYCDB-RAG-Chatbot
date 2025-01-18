import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()


class ClientManager:
    """
    ClientManager is a singleton class responsible for managing the initialization
    and access to various AI service clients and configuration details.
    """
    _instance = None

    def __new__(cls, *args, force_reinitialize=False, **kwargs):
        # Create a new instance only if one does not exist or if reinitialization is forced
        if cls._instance is None or force_reinitialize:
            cls._instance = super(ClientManager, cls).__new__(cls)
            cls._instance.initialize_clients(*args, **kwargs)
        return cls._instance

    def initialize_clients(self):
        """
        Initializes clients for Groq and VectorDB.
        """
        try:
            self.vector_store_path = os.environ.get("VECTOR_STORE")
            self.embedding_model = os.environ.get("EMBED_MODEL")
            self.LLM_model = os.environ.get("MODEL")
            self.client = Groq()
            self.json_file_path = os.environ.get("JSON_PATH")
            self.folder = os.environ.get("FILE_PATH")

        except Exception as e:
            print(f"Error initializing clients: {e}")
            raise

    def get_vector_store_path(self):
        return self.vector_store_path

    def get_embedding_model(self):
        return self.embedding_model

    def get_LLM_model(self):
        return self.LLM_model

    def get_client(self):
        return self.client

    def get_json_file_path(self):
        return self.json_file_path

    def get_folder(self):
        return self.folder