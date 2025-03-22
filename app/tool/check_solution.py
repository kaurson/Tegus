from app.tool.base import BaseTool


class CheckSolution(BaseTool):
    name: str = "check_solution"
    description: str = """Ask the user for a answer for the question/exercise asked in the last promt, do not output the answer.
"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "(required)Ask the user for a solution",
            },
        },
        "required": ["question"],
    }

    async def execute(self,question:str, **kwargs) -> str:
        print(question)
        user_input  = input("Sinu lahendus: ")
        return user_input
