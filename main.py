import gradio as gr
import warnings
from app.rag import RAGProcessor
import app.clients as client
from dotenv import load_dotenv
from typing import List, Tuple, Dict

# Load environment variables
load_dotenv()

class DocumentQASystem:
    def __init__(self):
        self.client_manager = client.ClientManager()
        self.rag_processor_instance = RAGProcessor(self.client_manager)

    def process_query(self, message: str, chat_history: List[Tuple[str, str]]) -> Tuple[str, List[Tuple[str, str]], Dict]:
        try:
            response, retrieval_details = self.rag_processor_instance.rag_query_with_explanation(message, chat_history)
            explanation = {
                "chunks_retrieved": len(retrieval_details["chunks"]),
                "relevant_files": list(set(chunk["source"] for chunk in retrieval_details["chunks"])),
                "confidence_scores": [f"{score:.2f}" for score in retrieval_details["scores"]],
                "processing_steps": retrieval_details["steps"]
            }
            chat_history.append((message, response))
            return "", chat_history, explanation
        except Exception as e:
            error_response = f"Error processing query: {str(e)}"
            chat_history.append((message, error_response))
            return "", chat_history, {"error": error_response}

    def create_ui(self):
        with gr.Blocks() as demo:
            gr.Markdown("# NYC Property Records Q&A System")
            
            with gr.Row():
                with gr.Column(scale=2):
                    chatbot = gr.Chatbot(height=400, show_label=False, container=True, show_copy_button=True)
                    with gr.Row():
                        msg = gr.Textbox(label="Ask a question about NYC property records", placeholder="Type your question here...", scale=4)
                        submit_btn = gr.Button("Send", scale=1)
                    clear = gr.ClearButton([msg, chatbot])
                
                with gr.Column(scale=1):
                    gr.Markdown("### Retrieval Process Details")
                    retrieval_info = gr.JSON(label="How the answer was found", show_label=True)
            
            gr.Markdown("### Sample Questions")
            with gr.Row():
                sample_questions = [
                    "What's the most recent property transaction on Broadway?",
                    "Show me mortgage details for properties in Manhattan",
                    "What's the average sale price in Brooklyn last year?",
                    "List all property types in Queens"
                ]
                for question in sample_questions:
                    gr.Button(question).click(
                        lambda q=question: self.process_query(q, []),
                        inputs=[],
                        outputs=[msg, chatbot, retrieval_info]
                    )
            
            msg.submit(self.process_query, [msg, chatbot], [msg, chatbot, retrieval_info])
            submit_btn.click(self.process_query, [msg, chatbot], [msg, chatbot, retrieval_info])
        
        return demo

if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=UserWarning)
    system = DocumentQASystem()
    demo = system.create_ui()
    demo.launch(share=False)
