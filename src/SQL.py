import os

import mysql.connector


def convert_str_to_list(input_str):  # '[red, green]' -> ['red', 'green']
    return input_str.replace("[", "").replace("]", "").split(",")


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

        self.cursor_db.execute(query)

        self.db.commit()

        return f"{self.cursor_db.rowcount} record inserted."

    def select_where_from_table(self, table_name, columns: list, statement_value_pairs: dict,
                                single_result: bool = False,
                                result_is_list_in_str_format: bool = False,
                                comparison_symbol: str = '='):
        columns = str(columns).replace("[", "").replace("]", "").replace("'", "")
        query = f"SELECT {columns} FROM {table_name} WHERE "

        for i, (statement, value) in enumerate(statement_value_pairs.items()):
            if i != 0:
                query += ' AND '
            value_for_query = value if type(value) != str else f"'{value}'"
            query += f"{statement} {comparison_symbol} {value_for_query}".replace('\"', '\'')

        query += ";"

        self.cursor_db.execute(query)

        result = self.cursor_db.fetchall()

        if len(result) == 0:
            return None
        elif single_result:
            if result_is_list_in_str_format:
                return convert_str_to_list(result[0][0])
            else:
                return result[0][0]
        else:
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
        return self.select_where_from_table('information_schema.TABLES', ['AUTO_INCREMENT'],
                                            {'table_schema': self.db_name, 'table_name': table_name},
                                            single_result=True)

    def get_all_column_names(self, table_name) -> list:
        result = self.select_where_from_table('INFORMATION_SCHEMA.COLUMNS', ['COLUMN_NAME'], {'TABLE_NAME': table_name})
        result = [column[0] for column in result]
        return result  # e.g.: ['game_id', 'active_bots', 'created_at']

    def clear_temporary_tables(self, game_id: int):
        self.delete_where_from_table('players', {'game_id': game_id})
        self.delete_where_from_table('chips', {'game_id': game_id})
        self.delete_where_from_table('rounds', {'game_id': game_id})


if __name__ == '__main__':
    db = SQL("localhost", "root", "")
    print(f"games column: {db.get_all_column_names('games')}")
    print(
        f"active bots: {db.select_where_from_table('games', 'active_bots', {'game_id': 1}, single_result=True, result_is_list_in_str_format=True)}")
    print(f"duration: {db.select_where_from_table('games', 'duration', {'game_id': 1}, single_result=True)}")
    print(f"insert new game: {db.insert('games', {})}")
