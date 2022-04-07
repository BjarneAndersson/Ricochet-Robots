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

    def foreign_key_checks(self):
        sql_command = "SET FOREIGN_KEY_CHECKS=0;"

        self.cursor_db.execute(sql_command)

    def insert(self, table_name, value_one, value_two=None, value_three=None, value_four=None, value_five=None,
               value_six=None, value_seven=None, value_eight=None, value_nine=None, value_ten=None, value_eleven=None,
               value_twelve=None, value_thirteen=None, value_fourteen=None):
        fields_and_values = {
            "games": ["(board_configuration, unused_chips, active_bots, player_count)", "(%s, %s, %s, %s)"],
            "rounds": ["(chip)", "(%s)"],
            "players": ["(ip-address, name, score, chips)", "(%s, %s, %s, %s)"]
        }

        current_fields_and_values = fields_and_values[table_name]
        self.foreign_key_checks()

        sql_command = f"INSERT INTO {table_name} {current_fields_and_values[0]} VALUES {current_fields_and_values[1]}"
        val = [value_one, value_two, value_three, value_four, value_five, value_six, value_seven, value_eight,
               value_nine, value_ten, value_eleven, value_twelve, value_thirteen, value_fourteen]

        for i in val:
            if i == None:
                val = val[:val.index(i)]
                break
            else:
                if type(i) == bool:
                    index = val.index(i)
                    val[index] = int(i)
                    val[index] = str(val[index])
                else:
                    val[val.index(i)] = str(i)
        val = tuple(val)

        self.cursor_db.execute(sql_command, val)

        self.db.commit()

        return f"{self.cursor_db.rowcount} record inserted."

    def insert_game(self):
        pass

    def insert_round(self):
        self.foreign_key_checks()

        sql_command = "INSERT INTO players (game_id, ip_address, name, score, chips, solution) VALUES (%s, %s, %s, %s, %s, %s)"

        self.cursor_db.execute(sql_command, (game_id, ip_address, name, 0, "", -1))

        self.db.commit()

        return f"{self.cursor_db.rowcount} record inserted."

    def update_round(self, round_id, duration, best_solution, best_player_id):
        self.update_where_from_table('rounds', 'duration', duration, 'round_id', round_id)
        self.update_where_from_table('rounds', 'best_solution', best_solution, 'round_id', round_id)
        self.update_where_from_table('rounds', 'best_player_id', best_player_id, 'round_id', round_id)

    def insert_player(self, game_id, ip_address, name):
        self.foreign_key_checks()

        sql_command = "INSERT INTO players (game_id, ip_address, name, score, chips, solution) VALUES (%s, %s, %s, %s, %s, %s)"

        self.cursor_db.execute(sql_command, (game_id, ip_address, name, 0, "", -1))

        self.db.commit()

        return f"{self.cursor_db.rowcount} record inserted."

    def select_all_from_table(self, column, table_name):
        self.cursor_db.execute(f"SELECT {column} FROM {table_name}")

        myresult = self.cursor_db.fetchall()

        # for x in myresult:
        #     print(x)

        return myresult

    def select_where_from_table(self, column, table_name, statement, value, statement1=None, value1=None,
                                statement2=None, value2=None):
        sql = f"SELECT {column} FROM {table_name} WHERE {statement} = %s"
        val = (value,)

        if statement1 and value1:
            sql += f" AND {statement1} = %s"
            val = (value, value1)

        if statement2 and value2:
            sql += f" AND {statement2} = %s"
            val = (value, value1, value2)

        self.cursor_db.execute(sql, val)

        myresult = self.cursor_db.fetchall()

        # for x in myresult:
        #     print(x)

        return myresult

    def delete_where_from_table(self, table_name, statement, value, statement1=None, value1=None):
        sql = f"DELETE FROM {table_name} WHERE {statement} = %s"
        val = (value,)

        if statement1 and value1:
            sql += f" AND {statement1} = %s"
            val = (value, value1)

        self.cursor_db.execute(sql, val)

        self.db.commit()

        # print(self.cursor_db.rowcount, "record(s) deleted")
        return f"{self.cursor_db.rowcount} record(s) deleted."

    def update_where_from_table(self, table_name, statement_set, value_set, statement_where, value_where):
        sql = f"UPDATE {table_name} SET {statement_set} = %s WHERE {statement_where} = %s"
        val = (value_set, value_where)

        self.cursor_db.execute(sql, val)

        self.db.commit()

        # print(self.cursor_db.rowcount, "record(s) affected")
        return f"{self.cursor_db.rowcount} record(s) affected."

    def order_table(self, column, table_name, order_column, asc_or_desc, order_column1=None, asc_or_desc1=None):
        sql = f"SELECT {column} FROM {table_name} ORDER BY {order_column} %s"
        val = (asc_or_desc,)

        if order_column1 and asc_or_desc1:
            sql += f", {order_column1} %s"
            val = (asc_or_desc, asc_or_desc1)

        self.cursor_db.execute(sql, val)

        myresult = self.cursor_db.fetchall()

        return myresult

    def count_entries_from_table(self, entry, table_name, statement, value, statement1=None, value1=None):
        sql = f"SELECT COUNT({entry}) from {table_name} WHERE {statement} = %s"
        val = (value,)

        if statement1 and value1:
            sql += f" AND {statement1} = %s"
            val = (value, value1)

        print(sql)
        self.cursor_db.execute(sql, val)

        self.db.commit()

        # print(self.cursor_db.rowcount, "record(s) affected")
        return self.cursor_db.fetchone()[0]

    def get_next_id(self, table_name):
        self.cursor_db.execute(
            f"SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE table_schema = '{self.db_name}' AND table_name = '{table_name}';")

        return self.cursor_db.fetchall()[0][0]

    def clear_table(self, table_name):
        self.cursor_db.execute(f"TRUNCATE TABLE {table_name}")

    def clear_temporary_tables(self):
        self.clear_table('players')
        self.clear_table('rounds')

    def clear_all_tables(self):
        self.clear_table('players')
        self.clear_table('games')
