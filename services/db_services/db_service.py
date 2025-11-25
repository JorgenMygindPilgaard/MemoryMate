import sqlite3
from pathlib import Path
from typing import Any, Iterable, Sequence

class Database:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        # Ensure folder exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_db()

    def _ensure_db(self):
        # Just opening once ensures the file exists
        with sqlite3.connect(self.db_path) as conn:
            pass

    def _get_connection(self):
        # Row factory returns sqlite3.Row (dict-like)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_table(self, table_name: str, columns_sql: str) -> None:
        """
        Create a table with given SQL column definitions.
        Example columns_sql: "id INTEGER PRIMARY KEY, name TEXT, age INTEGER"
        """
        with self._get_connection() as conn:
            cur = conn.cursor()
            sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
            cur.execute(sql)
            conn.commit()

    def create_index(self, index_name: str, table_name: str, columns: str, unique: bool = False) -> None:
        """
        Create an index on the given table and columns.
        Example: create_index("idx_users_name", "users", "name")
        """
        with self._get_connection() as conn:
            cur = conn.cursor()
            unique_sql = "UNIQUE " if unique else ""
            sql = f"CREATE {unique_sql}INDEX IF NOT EXISTS {index_name} ON {table_name} ({columns})"
            cur.execute(sql)
            conn.commit()

    def insert_rows(self, table_name: str, rows: list[dict[str, Any]]) -> int:
        """
        Insert multiple rows into a table.
        Rows may have different keys; missing columns are filled with NULL.
        Returns the number of rows inserted.
        """
        if not rows:
            return 0

        # 1. Collect all unique keys (columns)
        all_columns = set()
        for row in rows:
            all_columns.update(row.keys())
        columns = sorted(all_columns)  # sorted for consistent column order

        # 2. Prepare SQL
        placeholders = ", ".join("?" for _ in columns)
        cols = ", ".join(columns)
        sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"

        # 3. Convert each dict to tuple of values, filling missing keys with None
        values_list = []
        for row in rows:
            values_list.append(tuple(row.get(col, None) for col in columns))

        # 4. Execute in one batch
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.executemany(sql, values_list)
            conn.commit()
            return cur.rowcount

    def search(
        self,
        select: str = "*",
        from_: str = "",
        where: str = "",
        order_by: str = "",
        limit: int | None = None,
        params: Iterable[Any] = ()
    ) -> list[dict[str, Any]]:
        """
        Execute a SELECT query with separate clauses, return list of dicts.
        """
        if not from_:
            raise ValueError("FROM clause must be specified.")

        sql_parts = [f"SELECT {select}", f"FROM {from_}"]
        if where:
            sql_parts.append(f"WHERE {where}")
        if order_by:
            sql_parts.append(f"ORDER BY {order_by}")
        if limit is not None:
            sql_parts.append(f"LIMIT {limit}")

        sql = " ".join(sql_parts)

        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, tuple(params))
            rows = cur.fetchall()
            return [dict(row) for row in rows]

    def update_rows(
        self,
        table_name: str,
        updates: dict[str, Any],
        where: str = "",
        params: Iterable[Any] = ()
    ) -> int:
        """
        Update rows in a table. Returns number of rows affected.
        updates: dict of column -> new value
        """
        with self._get_connection() as conn:
            cur = conn.cursor()
            set_clause = ", ".join(f"{col} = ?" for col in updates.keys())
            sql = f"UPDATE {table_name} SET {set_clause}"
            if where:
                sql += f" WHERE {where}"
            all_params = tuple(updates.values()) + tuple(params)
            cur.execute(sql, all_params)
            conn.commit()
            return cur.rowcount

    def delete_rows(
        self,
        table_name: str,
        where: str = "",
        params: Iterable[Any] = ()
    ) -> int:
        """
        Delete rows in a table. Returns number of rows deleted.
        If where is empty, deletes all rows (use with caution).
        """
        with self._get_connection() as conn:
            cur = conn.cursor()
            sql = f"DELETE FROM {table_name}"
            if where:
                sql += f" WHERE {where}"
            cur.execute(sql, tuple(params))
            conn.commit()
            return cur.rowcount


