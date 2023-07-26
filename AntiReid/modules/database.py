import sqlite3

from telebot import types


class DataBase:


    def __init__(self):
        with sqlite3.connect("AntiReid.db") as connection:
            thread_cursor = connection.cursor()
            thread_cursor.execute(f"""CREATE TABLE IF NOT EXISTS channels(
                chat_id TEXT,
                title TEXT,
                username TEXT,
                owner_id INT,
                uid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE
            )""")
            connection.commit()

            thread_cursor.execute(f"""CREATE TABLE IF NOT EXISTS admins(
                chat_id TEXT,
                user_id INT,
                fullname TEXT,
                uid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE
            )""")
            connection.commit()

            thread_cursor.execute(f"""CREATE TABLE IF NOT EXISTS config(
                    chat_id TEXT,
                    max_flags INT,
                    tick_rate INT,
                    uid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE
                )""")
            connection.commit()

            thread_cursor.execute(f"""CREATE TABLE IF NOT EXISTS subs(
                chat_id TEXT,
                date_start TEXT,
                date_end TEXT,
                uid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE
            )""")
            connection.commit()


    @staticmethod
    def get_channel_id(owner_id: int):
        with sqlite3.connect("AntiReid.db") as connection:
            thread_cursor = connection.cursor()
            select = thread_cursor.execute(f"""SELECT * FROM channels WHERE owner_id = {owner_id}""").fetchone()
            return select

    @staticmethod
    def get_channel(chat_id: int):
        with sqlite3.connect("AntiReid.db") as connection:
            thread_cursor = connection.cursor()
            select = thread_cursor.execute(f"""SELECT * FROM channels WHERE chat_id = '{chat_id}'""").fetchone()
            return select

    @staticmethod
    def add_admin(chat_id: int, user: types.User):
        with sqlite3.connect("AntiReid.db") as connection:
            thread_cursor = connection.cursor()
            check = thread_cursor.execute(f"""SELECT * FROM admins WHERE chat_id = '{chat_id}' AND user_id = {user.id}""").fetchone()
            if check is not None:
                return

            thread_cursor.execute(f"""INSERT INTO admins VALUES (?, ?, ?, ?)""", (chat_id, user.id, user.full_name, None))
            connection.commit()

    @staticmethod
    def delete_admin(chat_id: int, user: types.User):
        with sqlite3.connect("AntiReid.db") as connection:
            thread_cursor = connection.cursor()
            check = thread_cursor.execute(
                f"""SELECT * FROM admins WHERE chat_id = '{chat_id}' AND user_id = {user.id}""").fetchone()
            if check is None:
                return

            thread_cursor.execute(f"""DELETE FROM admins WHERE chat_id = '{chat_id}' AND user_id = {user.id}""")
            connection.commit()


    @staticmethod
    def add_config(chat_id: int, max_flags: int, tick_rate: int):
        with sqlite3.connect("AntiReid.db") as connection:
            thread_cursor = connection.cursor()
            thread_cursor.execute(f"""INSERT INTO config VALUES (?, ?, ?, ?)""", (chat_id, max_flags, tick_rate, None))
            connection.commit()


    @staticmethod
    def update_config(chat_id: int, max_flags: int = None, tick_rate: int = None):
        if max_flags:
            update_type = ["max_flags", max_flags]
        else:
            update_type = ["tick_rate", tick_rate]

        with sqlite3.connect("AntiReid.db") as connection:
            thread_cursor = connection.cursor()
            thread_cursor.execute(f"""UPDATE config SET {update_type[0]} = {update_type[1]} WHERE chat_id = '{chat_id}'""")
            connection.commit()


    @staticmethod
    def get_config(chat_id: int):
        with sqlite3.connect("AntiReid.db") as connection:
            thread_cursor = connection.cursor()
            config = thread_cursor.execute(f"""SELECT * FROM config WHERE chat_id = '{chat_id}'""").fetchone()
            return config