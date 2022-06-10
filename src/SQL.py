import os

import mysql.connector
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
        except mysql.connector.errors.DatabaseError:
            raise RuntimeError("Can't connect to database")

        self.cursor = self.db.cursor()

    def insert(self, table_name, column_value_pairs: dict):
        if len(column_value_pairs) != 0:  # dict not empty
            columns = str(list(column_value_pairs.keys())).replace("[", "(").replace("]", ")").replace("\"",
                                                                                                       "").replace(
                "\'", "")  # ['x', 'y'] -> (x, y)
            values = str(list(column_value_pairs.values())).replace("[", "(").replace("]", ")").replace("\"",
                                                                                                        "\'")  # [2, "3"] -> (2, '3')
            query = f"INSERT INTO {table_name} {columns} VALUES {values};"
        else:  # column_value_pairs = {}
            columns = self.get_all_column_names(table_name)
            values = []

            for column in columns:
                values.append(f"Default({column})")

            columns = str(columns).replace("[", "(").replace("]", ")").replace("\"", "").replace("\'",
                                                                                                 "")  # ['x', 'y'] -> (x, y)
            values = str(values).replace("[", "(").replace("]", ")").replace("\'",
                                                                             "")  # ['Default(game_id)', 'Default(active_bots)'] -> (Default(game_id), Default(active_bots))

            query = f"INSERT INTO {table_name} {columns} VALUES {values};"

        self.cursor.execute(query)

        self.db.commit()

        result = self.cursor.fetchall()
        return result

    def execute_query(self, query: str):
        if not query.endswith(";"):
            query += ";"
        print(query)
        self.cursor.execute(query)

        self.db.commit()

        result = self.cursor.fetchall()
        return result

    # ------------------------------------------------------------------------------------------------------------------
    def get_all_column_names(self, table_name) -> list:
        result = self.execute_query(
            f"SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE table_name='{table_name}'")
        result = [column[0] for column in result]
        return result  # e.g.: ['game_id', 'active_bots', 'created_at']

    def close(self):
        self.db.close()


if __name__ == '__main__':
    db = SQL("localhost", 'root', 'root')
    db.close()
