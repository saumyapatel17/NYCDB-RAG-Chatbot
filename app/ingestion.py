import os
from typing import Tuple, List
from app.config import BATCH_SIZE
from app.preProcessing import DocumentProcessor

class DocumentIngestor:
    """
    A class to handle document ingestion, including reading, chunking, and inserting documents 
    into a ChromaDB collection.
    """

    def __init__(self):
        self.document_processor_instance = DocumentProcessor()

    def process_csv_with_metadata(self, csv_path: str, metadata_path: str) -> Tuple[List, List, List]:
        """
        Process a CSV file and its metadata file.
        """
        try:
            content = self.document_processor_instance.read_csv_with_metadata(csv_path, metadata_path)
            chunks = self.document_processor_instance.chunking(content)
            
            # Generate metadata for storage
            file_name = os.path.basename(csv_path)
            metadatas = [
                {
                    "source": file_name,
                    "chunk": i,
                    "content_type": "csv_with_metadata",
                    "metadata_file": os.path.basename(metadata_path)
                }
                for i in range(len(chunks))
            ]
            
            ids = [f"{file_name}_chunk_{i}" for i in range(len(chunks))]
            return ids, chunks, metadatas
        
        except Exception as e:
            raise Exception(f"Error processing CSV with metadata: {e}")

    def insert_documents_into_collection(self, collection, ids, texts, metadatas):
        """
        Inserts documents into the ChromaDB collection in batches.
        Args:
            collection: The ChromaDB collection to insert documents into.
            ids (list): A list of document chunk ids.
            texts (list): A list of document chunks.
            metadatas (list): A list of metadata dictionaries.
        """
        if not texts:
            return

        try:
            for i in range(0, len(texts), BATCH_SIZE):
                end_idx = min(i + BATCH_SIZE, len(texts))
                collection.add(
                    documents=texts[i:end_idx],
                    metadatas=metadatas[i:end_idx],
                    ids=ids[i:end_idx]
                )
        except Exception as e:
            raise Exception(f"Error inserting documents into collection: {e}") from e

    def ingest_documents(self, collection, file_path: str, metadata_path: str):
        """
        Processes and ingests all documents from a specified folder into a ChromaDB collection.
        """
        try:
            ids, texts, metadatas = self.process_csv_with_metadata(file_path, metadata_path)
            self.insert_documents_into_collection(collection, ids, texts, metadatas)
        except Exception as e:
            raise Exception(f"Error ingesting documents: {e}") from e
