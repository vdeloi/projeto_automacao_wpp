import sqlite3
import os
from abc import ABC, abstractmethod
from typing import List

# ---------------------------------------------------------
# 1. CONTRATO ABSTRATO (Interface)
# ---------------------------------------------------------
class BaseClinicaRepository(ABC):
    """
    Interface abstrata exclusiva para persistência de dados da Clínica.
    Define o que o banco de dados da clínica precisa fazer, independente 
    de ser SQLite, PostgreSQL, etc.
    """

    @abstractmethod
    def check_availability(self, date: str, doctor: str) -> List[str]:
        """Verifica os horários já ocupados para uma data e médico específicos."""
        pass

    @abstractmethod
    def book_appointment(self, client_name: str, date: str, time: str, doctor: str) -> bool:
        """Agenda uma consulta médica. Retorna True se sucesso, False se ocupado."""
        pass

# ---------------------------------------------------------
# 2. IMPLEMENTAÇÃO CONCRETA (SQLite)
# ---------------------------------------------------------
class SQLiteClinicaRepository(BaseClinicaRepository):
    """
    Implementação em SQLite do repositório da Clínica.
    Todo o código de acesso a dados deste tenant fica isolado aqui.
    """

    def __init__(self, db_path: str = "data/tenants/clinica_01/clinica.db"):
        self.db_path = db_path
        # Cria a pasta do banco da clínica se não existir
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._create_table()

    def _get_connection(self) -> sqlite3.Connection:
        """Abre a conexão isolada com o banco da clínica."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_table(self) -> None:
        """Cria a tabela de agendamentos com proteção contra horário duplo."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_name TEXT NOT NULL,
                    appointment_date TEXT NOT NULL,
                    appointment_time TEXT NOT NULL,
                    doctor TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(appointment_date, appointment_time, doctor)
                );
            """)

    def check_availability(self, date: str, doctor: str) -> List[str]:
        """Busca no banco os horários já preenchidos."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT appointment_time FROM appointments 
                WHERE appointment_date = ? AND doctor = ? 
                ORDER BY appointment_time;
                """,
                (date, doctor)
            )
            rows = cursor.fetchall()
            return [row["appointment_time"] for row in rows]

    def book_appointment(self, client_name: str, date: str, time: str, doctor: str) -> bool:
        """Tenta inserir o agendamento. Retorna False se houver conflito de horário."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO appointments (client_name, appointment_date, appointment_time, doctor)
                    VALUES (?, ?, ?, ?);
                    """,
                    (client_name, date, time, doctor)
                )
            return True
        except sqlite3.IntegrityError:
            # Captura a falha do banco se o UNIQUE for violado (horário já ocupado)
            return False