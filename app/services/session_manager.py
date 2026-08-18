from typing import List, Dict, Optional, Any
from app.repositories.base import BaseSessionRepository
from app.repositories.sqlite_repository import SQLiteSessionRepository


class SessionManager:
    """
    Gerenciador de Sessões de Atendimento.
    Intermedeia a comunicação e garante compatibilidade com os endpoints legados.
    """

    def __init__(self, repository: Optional[BaseSessionRepository] = None):
        self.repository: BaseSessionRepository = repository or SQLiteSessionRepository()

    def add_message(self, *args: Any, **kwargs: Any) -> None:
        """Extrai os dados da mensagem independentemente de como o endpoint envia."""
        phone_number = kwargs.get('phone_number') or kwargs.get('session_id')
        tenant_id = kwargs.get('tenant_id') or "default"
        role = kwargs.get('role')
        content = kwargs.get('content')

        # Fallback caso tenham sido enviados como argumentos posicionais
        if len(args) >= 1 and not phone_number: phone_number = args[0]
        if len(args) >= 2 and not tenant_id: tenant_id = args[1]
        if len(args) >= 3 and not role: role = args[2]
        if len(args) >= 4 and not content: content = args[3]

        if phone_number is not None and role is not None and content is not None:
            self.repository.save_message(str(phone_number), tenant_id, role, content)

    def get_history(self, *args: Any, **kwargs: Any) -> List[Dict[str, str]]:
        phone_number = kwargs.get('phone_number') or kwargs.get('session_id')
        tenant_id = kwargs.get('tenant_id') or "default"
        limit = kwargs.get('limit', 10)

        if len(args) >= 1 and not phone_number: phone_number = args[0]

        if phone_number is not None:
            return self.repository.get_history(str(phone_number), tenant_id, limit=limit)
        return []

    def save_interaction_id(self, *args: Any, **kwargs: Any) -> None:
        """Intercepta o salvamento do ID da interação sem quebrar a aplicação."""
        phone_number = kwargs.get('phone_number') or kwargs.get('session_id')
        interaction_id = kwargs.get('interaction_id')
        tenant_id = kwargs.get('tenant_id') or "default"

        if len(args) >= 1 and not phone_number: phone_number = args[0]
        if len(args) >= 2 and not interaction_id: interaction_id = args[1]

        if phone_number is not None and interaction_id is not None:
            self.repository.save_interaction_id(str(phone_number), str(interaction_id), tenant_id)

    def get_last_interaction_id(self, *args: Any, **kwargs: Any) -> Optional[str]:
        phone_number = kwargs.get('phone_number') or kwargs.get('session_id')
        tenant_id = kwargs.get('tenant_id') or "default"

        if len(args) >= 1 and not phone_number: phone_number = args[0]

        if phone_number is not None:
            return self.repository.get_last_interaction_id(str(phone_number), tenant_id)
        return None

    def clear_session(self, *args: Any, **kwargs: Any) -> None:
        phone_number = kwargs.get('phone_number') or kwargs.get('session_id')
        tenant_id = kwargs.get('tenant_id') or "default"

        if len(args) >= 1 and not phone_number: phone_number = args[0]

        if phone_number is not None:
            self.repository.clear_session(str(phone_number), tenant_id)


# Instância global utilizada pelos endpoints da API e pelos Agentes
session_manager = SessionManager()