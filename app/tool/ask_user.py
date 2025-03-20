from app.tool.base import BaseTool


class AskUser(BaseTool):
    name: str = "ask_user"
    description: str = """You can ask the user for input, use this tool to ask the user for further questions. Use this tool mainly to confirm if the user understood the explenation.
"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "(required)The question to be asked from the user",
            },
        },
        "required": ["question"],
    }

    async def execute(self,question:str, **kwargs) -> str:
        print(question)
        user_input  = input("Sinu vastus:")
        return user_input