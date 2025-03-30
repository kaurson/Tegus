from app.tool.base import BaseTool
from supabase import create_client, Client
from datetime import datetime
from typing import Optional
from pydantic import Field
import uuid
import asyncio
import os
from dotenv import load_dotenv, find_dotenv

# Constants (only what's needed for Supabase)
load_dotenv(find_dotenv())

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

class CheckSolution(BaseTool):
    name: str = "check_solution"
    description: str = """Generate an answer to the provided question/exercise using an LLM 
    and store the question and answer in the database."""
    session_id: Optional[str] = None

    parameters: dict = {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "(required) The question or exercise to be answered by the LLM",
            },
            "session_id": {
                "type": "string",
                "description": "The session ID this step belongs to.",
            },
            "step_index": {
                "type": "integer",
                "description": "The current step index as a number (0-based)",
            }
        },
        "required": ["question", "session_id", "step_index"],
    }
    
    supabase: Client = Field(default_factory=lambda: create_client(SUPABASE_URL, SUPABASE_KEY))

    async def execute(self, question: str, **kwargs) -> str:
        """
        Generates an answer to the question using an LLM and stores it in the database.

        Args:
            question: The question/exercise string
            **kwargs: Keyword arguments containing:
                - session_id: The UUID of the session
                - step_index: The current step index as a number (0-based)
        """
        # Extract and validate additional parameters
        session_id = kwargs.get("session_id")
        step_index = kwargs.get("step_index")

        if not all([question, session_id, step_index is not None]):
            print(f"Missing parameters: question={question}, session_id={session_id}, step_index={step_index}")
            return "Error: Missing required parameters"

        # Ensure step_index is an integer
        try:
            step_index = int(step_index)
        except (ValueError, TypeError):
            print(f"Invalid step_index: {step_index}")
            return "Error: step_index must be a number"

        # Validate session_id format (UUID)
        try:
            uuid.UUID(session_id)
        except ValueError:
            print(f"Invalid session_id: {session_id}")
            return "Error: session_id must be a valid UUID"

        # Store session_id for later use
        self.session_id = session_id

        # Generate the answer using the LLM
        llm_answer = await self._get_llm_answer(question)

        # Store the question and LLM-generated answer in the database
        await self._store_result(session_id, step_index, question, llm_answer)

        return llm_answer

    async def _get_llm_answer(self, question: str) -> str:
        """Generate an answer to the question using an LLM."""
        try:
            # Import necessary modules for LLM interaction
            from app.schema import Message
            from app.llm import LLM

            # Create a system message to guide the LLM
            system_msg = Message.system_message(
                """You are an expert physics education assistant that provides precise, accurate, and well-structured answers in Estonian.
                Follow these guidelines:
                1. Answer Structure:
                - Keep answers concise (max 30 words)
                - Focus on key physics concepts
                - Use proper Estonian scientific terminology
                - Include relevant formulas when applicable
                
                2. Educational Focus:
                - Emphasize understanding over memorization
                - Connect concepts to real-world examples
                - Use clear, student-friendly language
                - Break down complex ideas into simple parts
                
                3. Quality Standards:
                - Ensure scientific accuracy
                - Use appropriate physics terminology
                - Provide practical examples
                - Make connections to related concepts
                
                4. Language and Style:
                - Write in clear, proper Estonian
                - Use active voice
                - Keep sentences short and clear
                - Avoid unnecessary technical jargon"""
            )
            
            # Create a user message with the question
            user_msg = Message.user_message(
                f"""Palun vasta järgmisele füüsikaküsimusele: {question}

                Vasta järgides neid nõudeid:
                - Kasuta lühikest, selget keelt
                - Fokusseeru põhikontseptsioonidele
                - Lisa praktilisi näiteid
                - Kasuta õigeid füüsikatermineid
                - Piira vastust 30 sõnaga
                - Struktureeri vastus loogiliselt"""
            )
            
            # Initialize the LLM and get the answer
            llm = LLM()
            answer = await llm.ask(
                messages=[user_msg],
                system_msgs=[system_msg]
            )
            
            return answer.strip()
            
        except Exception as e:
            print(f"Error generating LLM answer: {e}")
            return "Error: Could not generate an answer"

    async def _store_result(self, session_id: str, step_index: int, question: str, answer: str) -> None:
        """Store the question and LLM-generated answer in the database with a specific format."""
        try:
            # First get the current lesson data
            response = self.supabase.table("Lessons").select("*").eq("session_id", session_id).execute()
            if not response.data:
                print(f"No lesson found for session_id: {session_id}")
                return
                
            lesson_data = response.data[0]
            step_responses = lesson_data.get("step_responses", [])
            
            # Ensure step_index is within bounds
            if step_index >= len(step_responses):
                print(f"Step index {step_index} is out of bounds")
                return
                
            # Get existing events
            existing_content = step_responses[step_index].get("content", {})
            existing_events = existing_content.get("events", [])
            
            # Create timestamp for the event
            timestamp = datetime.utcnow().isoformat()
            
            # New event structure with content and metadata
            new_event = {
                "event_type": "check_solution",
                "timestamp": timestamp,
                "content": {
                    "question": question,
                    "answer": answer
                },
    
            }
            
            # Update the specific step response
            step_responses[step_index].update({
                "status": "finished",
                "step_index": step_index,
                "content": {
                    "events": existing_events + [new_event]
                    
                }
            })
            
            # Update the entire step_responses array
            update_response = self.supabase.table("Lessons").update({
                "step_responses": step_responses
            }).eq("session_id", session_id).execute()
            
            if update_response.error:
                print(f"Error updating database: {update_response.error}")
                
        except Exception as e:
            print(f"Failed to store CheckSolution result: {e}")
            print(f"Session ID: {session_id}, Step Index: {step_index}")
            print(f"Response data: {response.data if 'response' in locals() else 'No response'}")