from telebot import TeleBot, types, util
from telebot.util import antiflood

from modules.database import DataBase


class Backend:

    def __init__(self, bot: TeleBot):
        self.bot = bot
        self.last_act = dict()

        self.bot.register_chat_member_handler(self.checker, func=lambda c: c.new_chat_member.status == "kicked")


    def checker(self, chat_member: types.ChatMemberUpdated):
        from_user_status = self.bot.get_chat_member(chat_member.chat.id, chat_member.from_user.id).status
        if from_user_status == "creator":
            return

        self.flag_user(chat_member)


    def flag_user(self, chat_member: types.ChatMemberUpdated):
        user_id = chat_member.from_user.id
        chat_id = chat_member.chat.id
        now_tick = chat_member.date

        config = DataBase.get_config(chat_id)

        max_flags = config[1]
        tick_rate = config[2]

        if max_flags == 1:
            self.reid_found(chat_member)
            return

        if user_id in self.last_act:
            last_data = self.last_act[user_id]
            flags = last_data[0]
            last_tick = last_data[1]

            if now_tick - last_tick <= tick_rate:
                flags += 1
                if flags == max_flags:
                    self.reid_found(chat_member)
                    return

                self.last_act[user_id] = [flags, now_tick]
                self.logger_flags(chat_member, flags, max_flags)
                return

        self.last_act[user_id] = [1, now_tick]
        self.logger_flags(chat_member, 1, max_flags)


    def logger_flags(self, chat_member: types.ChatMemberUpdated, flags: int, max_flags: int):
        text = f"<b>Подозрение на рейд</b>\n\n" \
               f"<b>Полное имя:</b> {chat_member.from_user.full_name}\n" \
               f"<b>UserName:</b> @{chat_member.from_user.username}\n" \
               f"<b>TelegramID:</b> id<code>{chat_member.from_user.id}</code>\n\n" \
               f"<b>Число предупреждений: {flags} из {max_flags}</b>"

        owner_id = DataBase.get_channel(chat_member.chat.id)[3]

        antiflood(self.bot.send_message, owner_id, text)


    def reid_found(self, chat_member: types.ChatMemberUpdated):
        text_2 = None
        try:
            antiflood(self.bot.ban_chat_member, chat_member.chat.id, chat_member.from_user.id)
        except:
            text_2 = f"<b>🚨 ОБНАРУЖЕН РЕЙДЕР 🚨</b>\n" \
                     f"<b>У бота отсутствуют нужные права для выдачи блокировки</b>\n" \
                     f"<b>Рейдер:</b> {chat_member.from_user.full_name} (@{chat_member.from_user.username})" \
                     f" [id{chat_member.from_user.id}]"


        text = f"🚨 <b>Обнаружен рейдер</b> 🚨\n\n" \
               f"<b>Полное имя:</b> {chat_member.from_user.full_name}\n" \
               f"<b>UserName:</b> @{chat_member.from_user.username}\n" \
               f"<b>TelegramID:</b> id<code>{chat_member.from_user.id}</code>"

        owner_id = DataBase.get_channel(chat_member.chat.id)[3]

        if text_2:
            text = text_2

        antiflood(self.bot.send_message, owner_id, text)