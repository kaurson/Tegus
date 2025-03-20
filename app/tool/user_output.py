import os

import aiofiles

from app.tool.base import BaseTool


class OutputUser(BaseTool):
    name: str = "output_user"
    description: str = """Output content to the user"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "(required) The output given to the user.",
            },
        },
        "required": ["output"],
    }

    async def execute(self, content:str, **kwargs) -> str:
        OKGREEN = '\033[92m'
        ENDC = '\033[0m'
        print(OKGREEN + content + ENDC)
        return 