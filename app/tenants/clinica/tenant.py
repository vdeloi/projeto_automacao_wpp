# app/tenants/clinica/tenant.py
from typing import List, Optional
from app.tenants.base import BaseTenant
from app.tools.base_tool import AppTool
from app.tenants.clinica.prompts import SYSTEM_INSTRUCTION
from app.tenants.clinica.tools import (
    tool_consultar_horarios,
    tool_registrar_agendamento
)

class ClinicaTenant(BaseTenant):
    def __init__(self) -> None:
        self._file_search_store_id: Optional[str] = None

    @property
    def tenant_id(self) -> str:
        return "clinica_01"

    @property
    def name(self) -> str:
        return "Clínica Odontológica Sorriso"

    @property
    def system_instruction(self) -> str:
        return SYSTEM_INSTRUCTION

    @property
    def file_search_store_id(self) -> Optional[str]:
        return self._file_search_store_id

    def get_tools(self) -> List[AppTool]:
        return [tool_consultar_horarios, tool_registrar_agendamento]