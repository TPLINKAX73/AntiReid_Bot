from telebot import types, TeleBot
from modules.database import DataBase


class BotMenu:

    def __init__(self, bot: TeleBot):
        self.bot = bot

        self.bot.register_message_handler(self.start, commands=['start', 'help', 'menu'])
        self.bot.register_message_handler(self.configurate_flags, commands=['max_flags', 'flags'])
        self.bot.register_message_handler(self.configurate_tick_rate, commands=['tick_rate', 'tick'])


    def start(self, message: types.Message):
        self.bot.delete_state(message.chat.id, message.from_user.id)

        text = "Hello World!"
        self.bot.reply_to(message, text)


    def configurate_flags(self, message: types.Message):
        text_1 = f"<b>Правильное использование:</b>\n" \
                 f"/max_flags 3 - <b>Устанавливает конфигурацию, при которой рейдера забанит после 3-его кика</b>\n\n" \
                 f"/max_flags 1 - <b>Устанавливает конфигурацию, при которой рейдера забанит сразу же после первого кика</b>"

        if " " not in message.text:
            self.bot.reply_to(message, text_1)
            return

        args = message.text.split()
        if len(args) != 2:
            self.bot.reply_to(message, text_1)
            return

        if not args[1].isdigit():
            self.bot.reply_to(message, text_1)
            return

        chat_id = DataBase.get_channel_id(message.from_user.id)[0]
        DataBase.update_config(chat_id, max_flags=int(args[1]))

        text_2 = f"<b>Установлено максимальное число предупреждений:</b> {args[1]}\n\n" \
                 f"<b>Не забудьте установить время сброса предупреждений:</b> /tick_rate"

        self.bot.reply_to(message, text_2)


    def configurate_tick_rate(self, message: types.Message):
        text_1 = f"<b>Правильное использование:</b>\n" \
                 f"/tick_rate 10 - <b>Устанавливает конфигурацию, при которой, число предупреждений сбрасывается за 10 секунд не активности</b>\n\n" \
                 f"/tick_rate 30 - <b>Устанавливает конфигурацию, при которой, число предупреждений сбрасывается за 30 секунд не активности</b>"

        if " " not in message.text:
            self.bot.reply_to(message, text_1)
            return

        args = message.text.split()
        if len(args) != 2:
            self.bot.reply_to(message, text_1)
            return

        if not args[1].isdigit():
            self.bot.reply_to(message, text_1)
            return

        chat_id = DataBase.get_channel_id(message.from_user.id)[0]
        DataBase.update_config(chat_id, tick_rate=int(args[1]))

        text_2 = f"<b>Установлено время сброса предупреждений:</b> {args[1]} сек.\n\n" \
                 f"<b>Не забудьте установить максимальное число предупреждений:</b> /max_flags"

        self.bot.reply_to(message, text_2)