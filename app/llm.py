import os
from typing import List, Tuple
from app.prompts import PROMPTS
from app.config import TEMPERATURE, MAX_TOKENS, TOP_P
from dotenv import load_dotenv
# Load environment variables
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv('GROQ_API_KEY')

class LLMProcessor:
    """
    A class to handle generating responses from an LLM model using Groq API.
    """

    def __init__(self, client_manager):
        self.LLM_model = client_manager.get_LLM_model()
        self.client = client_manager.get_client()

    def generate_response(self, query: str, context: str, chat_history: List[Tuple[str, str]]) -> str:
        """
        Generate a response considering chat history.
        """
        try:
            # Format chat history for context
            formatted_history = ""
            if chat_history:
                formatted_history = "\n".join([
                    f"Human: {h[0]}\nAssistant: {h[1]}" 
                    for h in chat_history[-3:]  # Include last 3 exchanges
                ])

            response = self.client.chat.completions.create(
                model=self.LLM_model,
                messages=[
                    {"role": "system", "content": PROMPTS.SYSTEM_PROMPT},
                    {"role": "user", "content": PROMPTS.CHAT_PROMPT.format(
                        query=query,
                        context=context,
                        chat_history=formatted_history
                    )}
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                top_p=TOP_P,
                stream=True,
                stop=None,
            )

            output = ""
            for chunk in response:
                output += chunk.choices[0].delta.content or ""

            return output

        except Exception as e:
            print(f"Error generating response: {e}")
            return "An error occurred while generating the response. Please try again later."
