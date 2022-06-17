import psycopg2
import mysql.connector


class MySQL:
    def __init__(self, host: str, username: str, password: str):
        self.host: str = host
        self.username: str = username
        self.password: str = password
        self.database_name: str = "ricochet_robots"

        self.db = None
        self.cursor = None

        self.connect_to_db()

    def connect_to_db(self):
        try:
            self.db = mysql.connector.connect(
                host=self.host,
                user=self.username,
                password=self.password,
                database=self.database_name
            )
        except mysql.connector.ProgrammingError:
            raise RuntimeError("Can't connect to database")

        self.cursor = self.db.cursor(buffered=True)

    def execute_query(self, query: str):
        if not query.endswith(";"):
            query += ";"

        if query.startswith("INSERT"):
            query = query.split(" RETURNING ")[0] + ";"
            self.cursor.execute(query)
            query = "SELECT LAST_INSERT_ID();"

        self.cursor.execute(query)

        self.db.commit()

        try:
            result = self.cursor.fetchall()
            return result
        except mysql.connector.errors.InterfaceError:
            return None

    def close(self):
        self.db.close()


class PostgreSQL:
    def __init__(self, host: str, username: str, password: str):
        self.host: str = host
        self.username: str = username
        self.password: str = password
        self.database_name: str = "ricochet_robots"
        self.port: int = 5432

        self.db = None
        self.cursor = None

        self.connect_to_db()

    def connect_to_db(self):
        try:
            self.db = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.username,
                password=self.password,
                database=self.database_name
            )
        except psycopg2.ProgrammingError:
            raise RuntimeError("Can't connect to database")

        self.cursor = self.db.cursor()

    def execute_query(self, query: str):
        if not query.endswith(";"):
            query += ";"
        self.cursor.execute(query)

        self.db.commit()

        try:
            result = self.cursor.fetchall()
            return result
        except psycopg2.ProgrammingError:
            return None

    def close(self):
        self.db.close()


if __name__ == '__main__':
    db = PostgreSQL("localhost", 'root', 'root')
    db.close()
