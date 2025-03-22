import json
import random
from app.tool.base import BaseTool  # Ensure this import exists

# Path to JSON file
JSON_PATH = "C:\\Users\\henri\\OneDrive\\Desktop\\tegus\\zzzz\\exercise.json"

class ExerciseGenerator(BaseTool):
    name: str = "exercise_search"
    description: str = "Search for physics exercises based on a query topic."
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The topic of the exercise, choose the most relevant one from these: [Mehhaanika, Kinemaatika, Lorentzi jõud]",
            },
        },
        "required": ["query"],
    }

    async def execute(self, **kwargs) -> list:
        """
        Searches exercises from a JSON file based on the given topic.

        Args:
            **kwargs: Keyword arguments, expecting 'query' as the topic.

        Returns:
            list: List of matching exercise questions.
        """
        # ✅ Get query text
        query_text = kwargs.get("query")
        if not query_text:
            return ["Error: 'query' parameter is required"]

        try:
            # ✅ Load exercises from JSON file
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                exercises = json.load(f)

            # ✅ Search for exercises matching the topic
            results = [ex for ex in exercises if query_text.lower() in ex["topic"].lower()]

            # ✅ Return results
            if results:
                return random.choice([f"Question: {ex['question']}, Solution for comparison: {ex['solution']}" for ex in results])
            else:
                return [f"No exercises found for topic: '{query_text}'"]

        except Exception as e:
            return [f"Error loading exercises: {str(e)}"]
