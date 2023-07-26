from telebot.handler_backends import State, StatesGroup
from telebot import TeleBot


class Admins(StatesGroup):
    uid = State()
    perms = State()


class StateHelper:

    def __init__(self, bot: TeleBot):
        self.bot = bot

    def save_data(self, user_id: int, chat_id: int, keys: list, values: list):
        with self.bot.retrieve_data(user_id, chat_id) as data:
            for index in range(len(keys)):
                data[keys[index]] = values[index]
        return True

    def get_data(self, user_id: int, chat_id: int, keys: list):
        result = dict()

        with self.bot.retrieve_data(user_id, chat_id) as data:
            for key in keys:
                result[key] = data[key]

        return result