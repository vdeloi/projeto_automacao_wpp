# app/services/session_manager.py

from typing import Dict, Optional


class SessionManager:
    """
    Gerenciador de memória das conversas com isolamento Multi-Tenant.
    Chave de armazenamento: 'tenant_id:phone_number'.
    """

    def __init__(self) -> None:
        # Exemplo: { "clinica_01:5511999999999": "interaction_id_123" }
        self._sessions: Dict[str, str] = {}

    def _make_key(self, tenant_id: str, phone_number: str) -> str:
        """Gera a chave única combinando empresa e telefone."""
        return f"{tenant_id}:{phone_number}"

    def get_last_interaction_id(self, tenant_id: str, phone_number: str) -> Optional[str]:
        """Recupera o último interaction_id deste cliente nesta empresa específica."""
        try:
            key = self._make_key(tenant_id, phone_number)
            interaction_id = self._sessions.get(key)
        except Exception as error:
            print(f"[AVISO] Erro ao recuperar sessão para {tenant_id}:{phone_number}: {error}")
            return None
        else:
            return interaction_id

    def save_interaction_id(self, tenant_id: str, phone_number: str, interaction_id: str) -> None:
        """Salva ou atualiza a sessão para este cliente nesta empresa."""
        try:
            key = self._make_key(tenant_id, phone_number)
            self._sessions[key] = interaction_id
        except Exception as error:
            print(f"[ERRO] Falha ao salvar sessão para {tenant_id}:{phone_number}: {error}")
        else:
            print(f"[DEBUG] Sessão atualizada para [{key}] -> ID: {interaction_id}")

    def clear_session(self, tenant_id: str, phone_number: str) -> None:
        """Limpa o histórico de uma conversa específica."""
        try:
            key = self._make_key(tenant_id, phone_number)
            if key in self._sessions:
                del self._sessions[key]
        except Exception as error:
            print(f"[ERRO] Falha ao resetar sessão de {key}: {error}")
        else:
            print(f"[DEBUG] Sessão resetada para [{key}].")


# Instância global
session_manager = SessionManager()