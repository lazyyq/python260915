import sqlite3
import sys
from pathlib import Path
from typing import Optional

class CustomerManager:
    """Customers 테이블의 생성, 조회, 수정, 삭제를 담당한다."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.initialize_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize_database(self) -> None:
        query = """
            CREATE TABLE IF NOT EXISTS Customers (
                custID INTEGER PRIMARY KEY AUTOINCREMENT,
                custName TEXT NOT NULL,
                custTitle TEXT NOT NULL
            )
        """
        with self._connect() as connection:
            connection.execute(query)

    def create_customer(self, name: str, title: str) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO Customers (custName, custTitle) VALUES (?, ?)",
                (name, title),
            )
            return int(cursor.lastrowid)

    def get_customers(self, keyword: Optional[str] = None) -> list[sqlite3.Row]:
        query = "SELECT custID, custName, custTitle FROM Customers"
        parameters: tuple[str, ...] = ()

        if keyword and keyword.strip():
            query += " WHERE custName LIKE ? OR custTitle LIKE ?"
            search_term = f"%{keyword.strip()}%"
            parameters = (search_term, search_term)

        query += " ORDER BY custID"
        with self._connect() as connection:
            return connection.execute(query, parameters).fetchall()

    def update_customer(self, cust_id: int, name: str, title: str) -> None:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE Customers
                SET custName = ?, custTitle = ?
                WHERE custID = ?
                """,
                (name, title, cust_id),
            )
            if cursor.rowcount == 0:
                raise ValueError("수정할 고객 정보를 찾을 수 없습니다.")

    def delete_customer(self, cust_id: int) -> None:
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM Customers WHERE custID = ?", (cust_id,)
            )
            if cursor.rowcount == 0:
                raise ValueError("삭제할 고객 정보를 찾을 수 없습니다.")

    def close(self) -> None:
        """각 작업마다 연결을 닫으므로 호환성을 위한 빈 메서드다."""