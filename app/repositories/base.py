from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class BaseSessionRepository(ABC):
    """
    Interface abstrata para persistência de sessões de chat.
    Define as operações obrigatórias para qualquer banco de dados.
    """

    @abstractmethod
    def save_message(self, session_id: str, tenant_id: str, role: str, content: str) -> None:
        """Salva uma nova mensagem no histórico da sessão."""
        pass

    @abstractmethod
    def get_history(self, session_id: str, tenant_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, str]]:
        """Recupera as últimas mensagens de uma sessão em ordem cronológica."""
        pass

    @abstractmethod
    def get_last_interaction_id(self, session_id: str, tenant_id: Optional[str] = None) -> Optional[str]:
        """Recupera o ID da última interação registrada."""
        pass

    @abstractmethod
    def save_interaction_id(self, session_id: str, interaction_id: str, tenant_id: Optional[str] = None) -> None:
        """Salva o ID da interação atual da sessão (útil para webhooks)."""
        pass

    @abstractmethod
    def clear_session(self, session_id: str, tenant_id: Optional[str] = None) -> None:
        """Remove o histórico de uma sessão."""
        pass