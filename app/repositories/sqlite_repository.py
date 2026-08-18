import sqlite3
import os
from typing import List, Dict, Optional
from app.repositories.base import BaseSessionRepository

class SQLiteSessionRepository(BaseSessionRepository):
    """
    Implementação concreta do repositório de sessões utilizando SQLite.
    """

    def __init__(self, db_path: str = "data/app_sessions.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._create_table()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_table(self) -> None:
        """Cria as tabelas de mensagens e de metadados caso não existam."""
        with self._get_connection() as conn:
            # Tabela de mensagens
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_tenant 
                ON chat_messages(session_id, tenant_id);
            """)
            
            # Nova tabela: Metadados da Sessão (para o interaction_id)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_metadata (
                    session_id TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    interaction_id TEXT,
                    PRIMARY KEY (session_id, tenant_id)
                );
            """)

    def save_message(self, session_id: str, tenant_id: str, role: str, content: str) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO chat_messages (session_id, tenant_id, role, content) 
                VALUES (?, ?, ?, ?);
                """,
                (session_id, tenant_id or "default", role, content)
            )

    def get_history(self, session_id: str, tenant_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, str]]:
        with self._get_connection() as conn:
            if tenant_id:
                cursor = conn.execute(
                    "SELECT role, content FROM chat_messages WHERE session_id = ? AND tenant_id = ? ORDER BY id DESC LIMIT ?;",
                    (session_id, tenant_id, limit)
                )
            else:
                cursor = conn.execute(
                    "SELECT role, content FROM chat_messages WHERE session_id = ? ORDER BY id DESC LIMIT ?;",
                    (session_id, limit)
                )
            rows = cursor.fetchall()
            return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]

    def get_last_interaction_id(self, session_id: str, tenant_id: Optional[str] = None) -> Optional[str]:
        """Lê o último interaction_id gravado na tabela de metadados."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT interaction_id FROM session_metadata WHERE session_id = ? AND tenant_id = ?;",
                (session_id, tenant_id or "default")
            )
            row = cursor.fetchone()
            return row["interaction_id"] if row else None

    def save_interaction_id(self, session_id: str, interaction_id: str, tenant_id: Optional[str] = None) -> None:
        """Salva ou atualiza o interaction_id na tabela de metadados."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO session_metadata (session_id, tenant_id, interaction_id)
                VALUES (?, ?, ?)
                ON CONFLICT(session_id, tenant_id) DO UPDATE SET interaction_id=excluded.interaction_id;
                """,
                (session_id, tenant_id or "default", interaction_id)
            )

    def clear_session(self, session_id: str, tenant_id: Optional[str] = None) -> None:
        with self._get_connection() as conn:
            if tenant_id:
                conn.execute("DELETE FROM chat_messages WHERE session_id = ? AND tenant_id = ?;", (session_id, tenant_id))
                conn.execute("DELETE FROM session_metadata WHERE session_id = ? AND tenant_id = ?;", (session_id, tenant_id))
            else:
                conn.execute("DELETE FROM chat_messages WHERE session_id = ?;", (session_id,))
                conn.execute("DELETE FROM session_metadata WHERE session_id = ?;", (session_id,))