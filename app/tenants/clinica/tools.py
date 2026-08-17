# app/tenants/clinica/tools.py

from app.tools.base_tool import AppTool


# Funções Python locais
def _consultar_horarios(data: str) -> str:
    print(f"[TOOL EXECUTADA - CLÍNICA] Consultando disponibilidade para: {data}")
    return f"Para a data {data}, temos horários disponíveis às 09:00, 14:00 e 16:30."


def _registrar_agendamento(nome_paciente: str, data: str, horario: str) -> str:
    print(f"[TOOL EXECUTADA - CLÍNICA] Agendando {nome_paciente} em {data} às {horario}")
    return f"Sucesso! A consulta de {nome_paciente} foi pré-agendada para o dia {data} às {horario}."


# Objetos AppTool estruturados com 'type': 'function'
tool_consultar_horarios = AppTool(
    name="consultar_horarios_disponiveis",
    description="Consulta os horários livres para atendimento odontológico em uma data específica.",
    parameters={
        "type": "object",
        "properties": {
            "data": {
                "type": "string",
                "description": "Data no formato DD/MM/AAAA (ex: '25/10/2026')."
            }
        },
        "required": ["data"]
    },
    handler=_consultar_horarios
)

tool_registrar_agendamento = AppTool(
    name="registrar_agendamento",
    description="Registra um agendamento de consulta odontológica para um paciente.",
    parameters={
        "type": "object",
        "properties": {
            "nome_paciente": {
                "type": "string",
                "description": "Nome completo do paciente."
            },
            "data": {
                "type": "string",
                "description": "Data da consulta (DD/MM/AAAA)."
            },
            "horario": {
                "type": "string",
                "description": "Horário desejado (ex: '14:00')."
            }
        },
        "required": ["nome_paciente", "data", "horario"]
    },
    handler=_registrar_agendamento
)