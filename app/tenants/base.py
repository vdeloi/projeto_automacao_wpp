# app/tenants/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.tools.base_tool import AppTool

class BaseTenant(ABC):
    """
    Classe Abstrata que define o contrato obrigatório para cada empresa.
    """
    @property
    @abstractmethod
    def tenant_id(self) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def system_instruction(self) -> str:
        pass

    @property
    def file_search_store_id(self) -> Optional[str]:
        """Identificador da FileSearchStore no Gemini (opcional)."""
        return None

    @abstractmethod
    def get_tools(self) -> List[AppTool]:
        """Retorna a lista de objetos AppTool desta empresa."""
        pass

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Retorna os esquemas de funções Python ('type': 'function')."""
        return [tool.to_gemini_schema() for tool in self.get_tools()]

    def get_all_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Retorna a lista completa de ferramentas para a API:
        Combina o File Search (RAG) do tenant com as funções Python locais.
        """
        schemas: List[Dict[str, Any]] = self.get_tool_schemas()
        
        if self.file_search_store_id:
            schemas.append({
                "type": "file_search",
                "file_search_store_names": [self.file_search_store_id]
            })
            
        return schemas

    def get_tool_map(self) -> Dict[str, AppTool]:
        """Retorna um dicionário {nome_da_funcao: AppTool} para execução rápida."""
        return {tool.name: tool for tool in self.get_tools()}