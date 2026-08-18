# app/tenants/clinica/tools.py

from app.tools.base_tool import AppTool
# Importamos o repositório isolado que criamos para a clínica
from app.tenants.clinica.repository import SQLiteClinicaRepository

# Inicializamos o banco de dados da clínica
clinica_repo = SQLiteClinicaRepository()

# ---------------------------------------------------------
# 1. Funções Python locais (Handlers do Banco de Dados)
# ---------------------------------------------------------

def _consultar_horarios(data: str, medico: str) -> str:
    print(f"[TOOL EXECUTADA - CLÍNICA] Consultando disponibilidade para: {data} com {medico}")
    
    # Busca os horários ocupados no banco de dados
    horarios_ocupados = clinica_repo.check_availability(data, medico)
    
    if not horarios_ocupados:
        return f"A agenda do(a) {medico} está totalmente livre no dia {data}. Pode oferecer qualquer horário comercial."
    
    # Transforma a lista de horários em uma string separada por vírgulas
    ocupados_str = ", ".join(horarios_ocupados)
    return f"No dia {data}, o(a) {medico} já tem consultas nos seguintes horários: {ocupados_str}. Os demais horários comerciais estão livres."


def _registrar_agendamento(nome_paciente: str, data: str, horario: str, medico: str) -> str:
    print(f"[TOOL EXECUTADA - CLÍNICA] Agendando {nome_paciente} em {data} às {horario} com {medico}")
    
    # Tenta salvar no banco de dados (retorna False se o horário já existir)
    sucesso = clinica_repo.book_appointment(nome_paciente, data, horario, medico)
    
    if sucesso:
        return f"Sucesso! A consulta de {nome_paciente} foi agendada para o dia {data} às {horario} com {medico}."
    else:
        return f"Erro: Infelizmente, o horário das {horario} no dia {data} com {medico} já está ocupado. Peça para o paciente escolher outro horário."

# ---------------------------------------------------------
# 2. Objetos AppTool estruturados com 'type': 'function'
# ---------------------------------------------------------

tool_consultar_horarios = AppTool(
    name="consultar_horarios_disponiveis",
    description="Consulta os horários ocupados e livres para atendimento médico/odontológico em uma data específica com um profissional específico.",
    parameters={
        "type": "object",
        "properties": {
            "data": {
                "type": "string",
                "description": "Data da consulta no formato DD/MM/AAAA (ex: '25/10/2026')."
            },
            "medico": {
                "type": "string",
                "description": "Nome do médico ou dentista desejado (ex: 'Dr. João')."
            }
        },
        "required": ["data", "medico"]
    },
    handler=_consultar_horarios
)

tool_registrar_agendamento = AppTool(
    name="registrar_agendamento",
    description="Registra um agendamento de consulta médica/odontológica para um paciente de forma definitiva.",
    parameters={
        "type": "object",
        "properties": {
            "nome_paciente": {
                "type": "string",
                "description": "Nome completo do paciente."
            },
            "data": {
                "type": "string",
                "description": "Data da consulta no formato DD/MM/AAAA."
            },
            "horario": {
                "type": "string",
                "description": "Horário desejado (ex: '14:00')."
            },
            "medico": {
                "type": "string",
                "description": "Nome do médico ou dentista responsável pelo atendimento."
            }
        },
        "required": ["nome_paciente", "data", "horario", "medico"]
    },
    handler=_registrar_agendamento
)