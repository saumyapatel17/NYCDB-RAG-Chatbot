# NYCDB RAG chatbot

The **NYCDB RAG chatbot** is a Retrieval-Augmented Generation (RAG)-based application that allows users to upload `.csv` documents and ask questions to gain insights. It integrates semantic search with language models to provide precise answers using only the uploaded content.

---

## Features

- **CSV Document Ingestion**: Supports `.csv` files for document upload.
- **Chunking and Vectorization**: Processes documents into meaningful chunks for efficient retrieval.
- **Semantic Search**: Retrieves the most relevant information based on the user's query.
- **Gradio Interface**: Interactive user interface for uploading files and querying.
- **Chat History**: Maintains a conversational flow for multiple questions.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/NYCDB-RAG-Chatbot.git
   cd NYCDB-RAG-Chatbot
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database with CSV files and metadata:
   ```bash
   python setupDB.py
   ```

---

## Usage

1. Run the main application to start the Gradio UI:
   ```bash
   python main.py
   ```
2. Open the Gradio interface in your browser (link provided in the terminal).
3. **Upload CSV Documents**: Drag and drop `.csv` files or use the upload button.
4. **Ask Questions**: Type your query in the chatbox to retrieve answers based on the document content.

---

## Ways to Improve Accuracy

1. **Query Expansion**: Broaden search terms to capture more relevant information.
2. **Improved Chunking**: Ensure documents are split meaningfully for better context retention.
3. **Enhanced Semantic Search**: Utilize advanced models like transformers for more precise retrieval.
4. **Re-ranking**: Prioritize search results based on relevance to the query.
5. **Post-processing of Responses**: Summarize and fact-check responses for clarity and accuracy.
6. **Feedback Loop**: Implement user feedback mechanisms to refine model responses over time.

---