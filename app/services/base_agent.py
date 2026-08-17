# app/services/base_agent.py

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    """
    Modelo de dados padronizado para representar a resposta de qualquer LLM.
    Garante o encapsulamento dos dados retornados para o restante do sistema.
    """
    text_output: str = Field(
        description="Texto final gerado pelo modelo para ser enviado ao utilizador."
    )
    interaction_id: Optional[str] = Field(
        default=None,
        description="Identificador único do turno/conversa mantido pelo provedor de IA."
    )
    tools_called: List[str] = Field(
        default_factory=list,
        description="Lista de nomes das funções/ferramentas executadas nesta interação."
    )
    raw_response: Optional[Any] = Field(
        default=None,
        description="Resposta bruta original retornada pela API (útil para debug)."
    )


class BaseLLMAgent(ABC):
    """
    Classe Abstrata de Agente (Contrato / Interface).
    Qualquer provedor de IA (Gemini, OpenAI, DeepSeek) DEVE herdar desta classe.
    """

    def __init__(self, model_name: str, system_instruction: Optional[str] = None):
        """
        Inicializa o agente base com o nome do modelo e instruções do sistema.
        """
        self.model_name = model_name
        self.system_instruction = system_instruction

    @abstractmethod
    def generate_interaction(
        self,
        user_input: str,
        previous_interaction_id: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        response_schema: Optional[Any] = None,
        **kwargs: Any
    ) -> AgentResponse:
        """
        Método abstrato principal para gerar uma interação multiturno.
        
        Parâmetros:
            user_input: A mensagem do cliente do WhatsApp.
            previous_interaction_id: O ID da interação anterior para manter a memória no servidor.
            tools: Lista de funções/ferramentas que o modelo pode chamar.
            response_schema: Esquema Pydantic para saídas estruturadas (JSON).
        """
        pass