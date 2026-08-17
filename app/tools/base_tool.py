# app/tools/base_tool.py

from typing import Callable, Dict, Any


class AppTool:
    """
    Encapsula a declaração de esquema exigida pela Interactions API ('type': 'function')
    e a função Python executável correspondente.
    """

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable[..., Any]
    ) -> None:
        self.name = name
        self.description = description
        self.parameters = parameters
        self.handler = handler

    def to_gemini_schema(self) -> Dict[str, Any]:
        """
        Retorna o dicionário no formato exato que a Interactions API exige.
        """
        return {
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }

    def execute(self, **kwargs: Any) -> Any:
        """Executa a função Python associada."""
        return self.handler(**kwargs)