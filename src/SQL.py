import os

import mysql.connector


class SQL:
    def __init__(self, host_id, user, password):
        self.host_id: str = host_id
        self.user: str = user
        self.password: str = password
        self.db_name: str = "ricochet_robots"

        self.db = None
        self.cursor_db = None

        self.connect_to_db()

    def connect_to_db(self):
        try:
            self.db = mysql.connector.connect(
                host=self.host_id,
                user=self.user,
                password=self.password,
                database=self.db_name
            )
        except mysql.connector.errors.DatabaseError:
            raise RuntimeError("Can't connect to database")

        self.cursor_db = self.db.cursor(buffered=True)
        self.cursor_db.execute("SET FOREIGN_KEY_CHECKS=0;")

    def insert(self, table_name, colum_value_pairs: dict):
        columns = str(list(colum_value_pairs.keys())).replace("[", "(").replace("]", ")").replace("\"", "").replace(
            "\'", "")  # ['x', 'y'] -> (x, y)
        values = str(list(colum_value_pairs.values())).replace("[", "(").replace("]", ")").replace("\"",
                                                                                                   "\'")  # [2, "3"] -> (2, '3')
        query = f"INSERT INTO {table_name} {columns} VALUES {values};"

        self.cursor_db.execute(query)

        self.db.commit()

        return f"{self.cursor_db.rowcount} record inserted."

    def select_where_from_table(self, table_name, column, statement_value_pairs: dict):
        query = f"SELECT {column} FROM {table_name} WHERE "

        for i, (statement, value) in enumerate(statement_value_pairs.items()):
            if i != 0:
                query += ' AND '
            query += f"{statement} = {value}".replace('\"', '\'')

        query += ";"

        self.cursor_db.execute(query)

        result = self.cursor_db.fetchall()[0][0]

        if type(result) == str and "[" in result:
            result = result.replace("[", "").replace("]", "").split(",")

        return result

    def update_where_from_table(self, table_name, statement_value_pair_set: dict, statement_value_pairs_where: dict):
        query = f"UPDATE {table_name} " \
                f"SET {list(statement_value_pair_set.keys())[0]} = {list(statement_value_pair_set.values())[0]} WHERE "

        for i, (statement, value) in enumerate(statement_value_pairs_where.items()):
            if i != 0:
                query += ' AND '
            query += f"{statement} = {value}".replace('\"', '\'')

        query += ";"

        self.cursor_db.execute(query)

        self.db.commit()

        return f"{self.cursor_db.rowcount} record(s) affected."

    def delete_where_from_table(self, table_name, statement_value_pairs):
        query = f"DELETE FROM {table_name} WHERE "

        for i, (statement, value) in enumerate(statement_value_pairs.items()):
            if i != 0:
                query += ' AND '
            query += f"{statement} = {value}".replace('\"', '\'')

        query += ";"

        self.cursor_db.execute(query)

        self.db.commit()

        # print(self.cursor_db.rowcount, "record(s) deleted")
        return f"{self.cursor_db.rowcount} record(s) deleted."

    def clear_table(self, table_name):
        self.cursor_db.execute(f"TRUNCATE TABLE {table_name}")
        self.db.commit()

    # ------------------------------------------------------------------------------------------------------------------
    def get_next_id(self, table_name):
        return self.select_where_from_table('information_schema.TABLES', 'AUTO_INCREMENT',
                                            {'table_schema': self.db_name, 'table_name': table_name})

    def clear_temporary_tables(self):
        self.clear_table('players')
        self.clear_table('rounds')

    def clear_all_tables(self):
        self.clear_table('games')
        self.clear_temporary_tables()


if __name__ == '__main__':
    db = SQL("localhost", "root", "")
    r = db.select_where_from_table('players', 'name', {'player_id': 82})
    print(f"Result: {r}")
