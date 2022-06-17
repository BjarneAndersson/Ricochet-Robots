import os

import psycopg2


def convert_str_to_list(input_str):  # '[red, green]' -> ['red', 'green']
    return input_str.replace("[", "").replace("]", "").split(",")


class SQL:
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
        except psycopg2.ProgrammingError as e:
            return None

    def close(self):
        self.db.close()


if __name__ == '__main__':
    db = SQL("localhost", 'root', 'root')
    db.close()
