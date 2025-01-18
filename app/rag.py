import json
import os
from typing import Dict, List, Tuple, Any
from app.initialiseDB import VectorDBSetup
from app.llm import LLMProcessor
from app.config import N_CHUNKS, CONFIDENCE_THRESHOLD

class RAGProcessor:
    """
    A class to handle Retrieval-Augmented Generation (RAG) operations, including 
    performing semantic searches, processing context, and generating responses.
    """

    def __init__(self, client_manager):
        self.json_file_path = client_manager.get_json_file_path()
        self.vector_db_instance = VectorDBSetup(client_manager)
        self.llm_processor_instance = LLMProcessor(client_manager)

    @staticmethod
    def semantic_search(collection, query: str, n_results: int = 2) -> dict:
        """
        Perform semantic search on the collection.
        Args:
            collection: The ChromaDB collection to search.
            query (str): The query to search for in the collection.
            n_results (int, optional): The number of results to retrieve. Defaults to 2.
        Returns:
            dict: The search results containing documents and distances.
        """
        return collection.query(query_texts=[query], n_results=n_results)

    @staticmethod
    def get_context(results: Dict) -> str:
        """
        Enhanced context retrieval with metadata-aware formatting.
        """
        documents = results['documents'][0]
        formatted_contexts = []

        for doc in documents:
            if "FILE METADATA:" in doc:
                # Split metadata and data sections
                metadata_section, data_section = doc.split("DATA RECORDS:")
                formatted_metadata = "Column Information:\n" + metadata_section.replace("FILE METADATA:", "").strip()
                formatted_data = "Data Records:\n" + data_section.strip()
                formatted_contexts.append(f"{formatted_metadata}\n\n{formatted_data}")
            else:
                formatted_contexts.append(doc)

        return "\n\n---\n\n".join(formatted_contexts)

    def save_qa_to_json(self, qa_data):
        try:
            if os.path.exists(self.json_file_path) and os.path.getsize(self.json_file_path) > 0:
                with open(self.json_file_path, 'r') as file:
                    qa_history = json.load(file)
            else:
                qa_history = []
                
            qa_history.append(qa_data)
            
            with open(self.json_file_path, 'w') as file:
                json.dump(qa_history, file, indent=4)
        except json.JSONDecodeError as e:
            print(f"Error reading JSON file: {e}")
            qa_history = [qa_data]  # Start fresh if file is corrupted
            with open(self.json_file_path, 'w') as file:
                json.dump(qa_history, file, indent=4)

    def extract_context_from_history(self, chat_history: List[Tuple[str, str]]) -> str:
        """
        Extract relevant context from chat history.
        """
        if not chat_history:
            return ""
            
        recent_exchanges = chat_history[-3:]  # Consider last 3 exchanges
        return "\n".join([
            f"Previous Q: {exchange[0]}\nA: {exchange[1]}"
            for exchange in recent_exchanges
        ])

    def enhance_query(self, query: str, is_metadata_query: bool, history_context: str) -> str:
        """
        Enhance the query with context and type-specific instructions.
        """
        base_query = query
        if history_context:
            base_query = f"Given this context from previous exchanges: {history_context}\n{query}"
            
        if is_metadata_query:
            return (f"Based on the column information and data provided, please answer: {base_query}. "
                   f"Include relevant metadata details in your response.")
        else:
            return (f"Based on the data records provided, please answer: {base_query}. "
                   f"Reference the column descriptions when relevant.")

    @staticmethod
    def extract_source_from_context(context: str) -> str:
        """
        Extract source file information from context.
        """
        if "FILE METADATA:" in context:
            return context.split("FILE METADATA:")[0].strip()
        return "Unknown source"

    def rag_query_with_explanation(self, query: str, chat_history: List[Tuple[str, str]]) -> Tuple[str, Dict[str, Any]]:
        """
        Enhanced RAG query with detailed explanation of the retrieval process.
        """
        try:
            collection = self.vector_db_instance.initialize_vectorDB()
            retrieval_details = {
                "steps": [],
                "chunks": [],
                "scores": [],
                "metadata_used": False
            }
            
            # Step 1: Query Analysis
            retrieval_details["steps"].append("Analyzing query type")
            metadata_query = any(term in query.lower() for term in 
                               ["metadata", "column", "field", "description", "data type", "what kind of"])
            retrieval_details["metadata_used"] = metadata_query

            # Step 2: Context from Chat History
            retrieval_details["steps"].append("Checking chat history for context")
            history_context = self.extract_context_from_history(chat_history)
            
            # Step 3: Semantic Search
            retrieval_details["steps"].append("Performing semantic search")
            n_results = N_CHUNKS * (2 if metadata_query else 1)
            results = self.semantic_search(collection, query, n_results)

            # Step 4: Context Filtering
            retrieval_details["steps"].append("Filtering relevant contexts")
            valid_contexts = []
            valid_scores = []
            for context, distance in zip(results['documents'][0], results['distances'][0]):
                if distance >= CONFIDENCE_THRESHOLD:
                    valid_contexts.append(context)
                    valid_scores.append(distance)
                    retrieval_details["chunks"].append({
                        "source": self.extract_source_from_context(context),
                        "score": distance
                    })
            
            retrieval_details["scores"] = valid_scores

            if not valid_contexts:
                return "Data Not Available", retrieval_details

            # Step 5: Context Combination
            retrieval_details["steps"].append("Combining contexts and generating response")
            context = self.get_context({
                'documents': [valid_contexts], 
                'distances': [valid_scores]
            })

            # Step 6: Query Enhancement
            enhanced_query = self.enhance_query(query, metadata_query, history_context)
            retrieval_details["steps"].append("Enhanced query with context and metadata awareness")

            # Step 7: Generate Response
            response = self.llm_processor_instance.generate_response(
                enhanced_query, 
                context,
                chat_history
            )

            # Save Q&A data
            qa_data = {
                "question": query,
                "answer": response,
                "query_type": "metadata" if metadata_query else "data",
                "retrieval_details": retrieval_details
            }
            self.save_qa_to_json(qa_data)

            return response, retrieval_details

        except Exception as e:
            error_message = f"Error during RAG query process: {str(e)}"
            retrieval_details["error"] = error_message
            print(error_message) 
            return "An error occurred while processing your query.", retrieval_details

    