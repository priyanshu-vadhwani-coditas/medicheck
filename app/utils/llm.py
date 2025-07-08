import os
import asyncio
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

load_dotenv()

def get_groq_api_key():
    """
    Retrieve the GROQ API key from environment variables.
    Raises an error if not set.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    return api_key

class GroqLLM:
    """
    Utility class for interacting with the Groq LLM via LangChain.
    """
    def __init__(self, model: str = "llama-3.3-70b-versatile", temperature: float = 0.5):
        """
        Initialize the LLM client with the specified model and temperature.
        """
        self.model = model
        self.temperature = temperature
        self.api_key = get_groq_api_key()
        self.llm = ChatGroq(
            groq_api_key=self.api_key,
            model_name=self.model,
            temperature=self.temperature
        )

    async def acall(self, prompt: str) -> str:
        """
        Async version of call method for concurrent processing.
        """
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        return response.content
