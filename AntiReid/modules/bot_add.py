import sqlite3

from telebot import types, TeleBot
from telebot.util import antiflood
from datetime import datetime
from modules.database import DataBase


class AntiReidBotAdd:


    def __init__(self, bot: TeleBot):
        self.bot = bot

        self.bot.register_my_chat_member_handler(self.invite_to_channel, func=lambda c: c.from_user.id != 6635088096 and c.old_chat_member.status == "left")
        self.bot.register_my_chat_member_handler(self.kick_from_channel, func=lambda c: c.from_user.id != 6635088096 and c.new_chat_member.status == "left")

        self.bot.register_chat_member_handler(self.add_member, func=lambda c: c.old_chat_member.status == "left" and c.new_chat_member.status == "member")
        self.bot.register_chat_member_handler(self.member_update_promote, func=lambda c: c.old_chat_member.status == "member" and c.new_chat_member.status == "administrator")
        self.bot.register_chat_member_handler(self.member_update_restrict, func=lambda c: c.old_chat_member.status == "administrator" and c.new_chat_member.status == "member")


    def invite_to_channel(self, chat_member: types.ChatMemberUpdated):
        try:
            text_1 = "<b>Внимание!</b>\n" \
                     "<b>Бота может добавить только создатель канала</b>\n"

            text_2 = "<b>Внимание!</b>\n" \
                     "<b>Боту для работы необходимо выдать следующие права:</b>\n" \
                     "  <b>[-]</b> Добавление администраторов\n" \
                     "  <b>[-]</b> Добавление участников"

            text_3 = "<b>Внимание!</b>\n" \
                     "<b>У Вас нет подписки на использование бота, чтобы приобрести её " \
                     "напишите сюда: <a href='https://t.me/chuitsboy'>Амин</a> (@chuitsboy)</b>"

            if not self.check_sub(chat_member):
                antiflood(self.bot.leave_chat, chat_member.chat.id)
                antiflood(self.bot.send_message, chat_member.from_user.id, text_3)
                return

            if not self.check_owner(chat_member):
                antiflood(self.bot.leave_chat, chat_member.chat.id)
                antiflood(self.bot.send_message, chat_member.from_user.id, text_1)
                return

            date = self.check_permissions(chat_member)
            if not date:
                antiflood(self.bot.leave_chat, chat_member.chat.id)
                antiflood(self.bot.send_message, chat_member.from_user.id, text_2)
                return

            self.save_to_database(chat_member)

            text_4 = f"<b>Бот успешно добавлен в канал</b>\n" \
                     f"<b>Окончание подписки:</b> <code>{datetime.fromtimestamp(float(date)).strftime('%d.%m.%Y')}</code>"
            antiflood(self.bot.send_message, chat_member.from_user.id, text_4)
        except Exception as e:
            print(e)
            return


    def kick_from_channel(self, chat_member: types.ChatMemberUpdated):
        username = chat_member.from_user.username
        if username is None:
            username = "нет_юзернейма"

        text = f"<b>Внимание!</b>\n" \
               f"<b>Бот был исключен из чата пользователем:</b> " \
               f"<a href='tg://user?id={chat_member.from_user.id}'>{chat_member.from_user.full_name}</a> " \
               f"(@{username})"

        with sqlite3.connect("AntiReid.db") as connection:
            thread_cursor = connection.cursor()
            owner_id = thread_cursor.execute(f"""SELECT owner_id FROM channels WHERE chat_id = '{chat_member.chat.id}'""").fetchone()

        if owner_id is None:
            return

        self.bot.send_message(owner_id, text)


    def add_member(self, chat_member: types.ChatMemberUpdated):
        text = f"{chat_member.from_user.full_name} (id{chat_member.from_user.id}) " \
               f"<b>добавил</b> {chat_member.new_chat_member.user.full_name} (id{chat_member.new_chat_member.user.id}) " \
               f"<b>в канал</b>"

        owner_id = DataBase.get_channel(chat_member.chat.id)[3]
        self.bot.send_message(owner_id, text)


    def kick_member(self, chat_member: types.ChatMemberUpdated):
        text = f"{chat_member.from_user.full_name} (id{chat_member.from_user.id}) " \
               f"<b>исключил</b> {chat_member.new_chat_member.user.full_name} (id{chat_member.new_chat_member.user.id}) " \
               f"<b>из канала</b>"

        owner_id = DataBase.get_channel(chat_member.chat.id)[3]
        self.bot.send_message(owner_id, text)


    def member_update_promote(self, chat_member: types.ChatMemberUpdated):
        text = f"{chat_member.from_user.full_name} (id{chat_member.from_user.id}) " \
               f"<b>назначил</b> {chat_member.new_chat_member.user.full_name} (id{chat_member.new_chat_member.user.id}) " \
               f"<b>администратором</b>"

        owner_id = DataBase.get_channel(chat_member.chat.id)[3]
        self.bot.send_message(owner_id, text)


    def member_update_restrict(self, chat_member: types.ChatMemberUpdated):
        text = f"{chat_member.from_user.full_name} (id{chat_member.from_user.id}) " \
               f"<b>снял</b> {chat_member.new_chat_member.user.full_name} (id{chat_member.new_chat_member.user.id}) " \
               f"<b>с должности администратора</b>"

        DataBase.delete_admin(chat_member.chat.id, chat_member.new_chat_member.user)
        owner_id = DataBase.get_channel(chat_member.chat.id)[3]
        self.bot.send_message(owner_id, text)


    def check_owner(self, chat_member: types.ChatMemberUpdated):
        status = self.bot.get_chat_member(chat_member.chat.id, chat_member.from_user.id).status
        if status != "creator":
            return False
        else:
            return True


    @staticmethod
    def check_permissions(chat_member: types.ChatMemberUpdated):
        if not (chat_member.new_chat_member.can_restrict_members and chat_member.new_chat_member.can_promote_members):
            return False
        return True


    @staticmethod
    def check_sub(chat_member: types.ChatMemberUpdated):
        chat_id = str(chat_member.chat.id)

        with sqlite3.connect("AntiReid.db") as connection:
            thread_cursor = connection.cursor()
            check = thread_cursor.execute(f"""SELECT date_end FROM subs WHERE chat_id = '{chat_id}'""").fetchone()

        if check is None:
            return False
        else:
            return check


    @staticmethod
    def save_to_database(chat_member: types.ChatMemberUpdated):
        chat_id = str(chat_member.chat.id)
        title = chat_member.chat.title
        username = chat_member.chat.username
        owner_id = chat_member.from_user.id

        with sqlite3.connect("AntiReid.db") as connection:
            thread_cursor = connection.cursor()
            thread_cursor.execute(f"""INSERT INTO channels VALUES (?, ?, ?, ?, ?)""", (chat_id, title, username, owner_id, None))
            connection.commit()