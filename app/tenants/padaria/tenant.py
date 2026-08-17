# app/tenants/padaria/tenant.py
from typing import List, Optional
from app.tenants.base import BaseTenant
from app.tools.base_tool import AppTool
from app.tenants.padaria.prompts import SYSTEM_INSTRUCTION
from app.tenants.padaria.tools import (
    tool_verificar_fornada,
    tool_calcular_taxa_entrega
)

class PadariaTenant(BaseTenant):
    def __init__(self) -> None:
        self._file_search_store_id: Optional[str] = None

    @property
    def tenant_id(self) -> str:
        return "padaria_01"

    @property
    def name(self) -> str:
        return "Padaria Pão Quente"

    @property
    def system_instruction(self) -> str:
        return SYSTEM_INSTRUCTION

    @property
    def file_search_store_id(self) -> Optional[str]:
        return self._file_search_store_id

    def get_tools(self) -> List[AppTool]:
        return [
            tool_verificar_fornada,
            tool_calcular_taxa_entrega
        ]