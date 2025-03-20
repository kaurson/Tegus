import asyncio
import os
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from app.tool.base import BaseTool

# Load environment variables
load_dotenv(find_dotenv())
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Constants
CHROMA_PATH = "/Users/kaur/PycharmProjects/OpenManus/tegus/chroma"
DATA_PATH = "/Users/kaur/PycharmProjects/OpenManus/tegus/data/documents"

class RagSearch(BaseTool):
    name: str = "rag_search"
    description: str = "A tool to retrieve data from a RAG model based on 9th grade physics."
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The query sent to the RAG model",
            },
        },
        "required": ["query"],
    }

    async def execute(self, **kwargs) -> list:
        """
        Performs a similarity search on the RAG database and returns relevant answers.
        
        Args:
            **kwargs: Keyword arguments, expecting 'query' as the query string
            
        Returns:
            list: List of answers extracted from the search results
        """
        # Extract query from kwargs
        query_text = kwargs.get("query")
        if not query_text:
            return ["Error: 'query' parameter is required"]

        # Prepare the database
        embedding_function = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
        
        # Search the database for relevant chunks
        try:
            results = db.similarity_search_with_relevance_scores(query_text, k=5)
            
            if not results or results[0][1] < 0.7:
                return [f"Unable to find matching results for '{query_text}'"]
            
            # Extract content from results
            content = [result[0].page_content for result in results]
            
            # Extract last word from each content piece            
            return content
            
        except Exception as e:
            return [f"Error occurred while processing the query: {str(e)}"]