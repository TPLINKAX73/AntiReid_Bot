import sqlite3

from telebot import types, TeleBot
from modules.bot_states import Admins, StateHelper
from telebot.util import antiflood
from modules.database import DataBase


class BotAdmins:

    def __init__(self, bot: TeleBot):
        self.bot = bot
        self.state_helper = StateHelper(bot)
        self.buttons = {
            'edit_channel': "Редактировать профиль канала",
            'send_message': "Публикация сообщений",
            'edit_message': "Удалять чужие посты",
            'add_members': "Добавление участников",
            'voice_chat': "Управление трансляциями",
            'add_admins': "Назначение админов"
        }
        self.perms = {
            'edit_channel': False,
            'send_message': True,
            'edit_message': False,
            'add_members': True,
            'voice_chat': False,
            'add_admins': False
        }
        self.perms_to_bot_perms = {
            'edit_channel': 'can_change_info',
            'send_message': 'can_post_messages',
            'edit_message': 'can_delete_messages',
            'add_members': 'can_invite_users',
            'voice_chat': 'can_manage_video_chats',
            'add_admins': 'can_promote_members'
        }

        self.bot.register_message_handler(self.add_admins_start, commands=['add_admin'])
        self.bot.register_message_handler(self.add_admin_uid, state=Admins.uid)

        self.bot.register_callback_query_handler(self.callback_perms, state=Admins.perms, func=lambda c: c.data.startswith("perm%"))


    def add_admins_start(self, message: types.Message):
        text = f"<b>Чтобы добавить администратора, следуйте одному из способов:</b>\n\n" \
               f"Если у пользователя разрешена пересылка в настройках конфиденциальности: <b>перешлите его любое сообщение</b>\n" \
               f"Если пользователь запустил бота (написал в лс /start): <b>напишите его @юзернейм</b>\n"

        self.bot.set_state(message.from_user.id, Admins.uid, message.chat.id)
        self.bot.reply_to(message, text)


    def add_admin_uid(self, message: types.Message):
        text = "<b>Выберите нужные права для пользователя..</b>"
        kb = self.generate_keyboard()

        text_1 = "<b>У пользователя стоят настройки конфиденциальности</b>\n" \
                 "Пожалуйста, попросите пользователя запустить бота (/start) и пришлите его @юзернейм"

        text_2 = "<b>USERNAME указан не верно</b>\n" \
                 "Правильное написание: @юзернейм"

        text_3 = "<b>TelegramID указан не верно</b>\n" \
                 "Правильное написание: id1234567890"

        text_4 = "<b>Пользователь не запустил бота, либо username указан неверно!</b>"
        text_5 = "<b>Пользователь не запустил бота, либо TelegramID указан неверно!</b>"

        if message.forward_from:
            try:
                self.bot.set_state(message.from_user.id, Admins.perms, message.chat.id)
                self.state_helper.save_data(message.from_user.id, message.chat.id, ['user_id'],
                                            [message.forward_from.id])
                self.bot.reply_to(message, text, reply_markup=kb)
                return
            except:
                self.bot.reply_to(message, text_1)
                return

        if message.text.startswith("@"):
            args = message.text.split("@")
            if len(args) != 2:
                self.bot.reply_to(message, text_2)
                return

            try:
                user_id = antiflood(self.bot.get_chat(args[1]).id)
            except:
                self.bot.reply_to(message, text_4)
                return

            self.bot.set_state(message.from_user.id, Admins.perms, message.chat.id)
            self.state_helper.save_data(message.from_user.id, message.chat.id, ['user_id'], [user_id])
            self.bot.reply_to(message, text, reply_markup=kb)
            return

        if message.text.startswith("id"):
            args = message.text.split("id")
            if len(args) != 2:
                self.bot.reply_to(message, text_3)
                return

            try:
                user_id_ = int(args[1])
                user_id = antiflood(self.bot.get_chat(user_id_).id)
            except:
                self.bot.reply_to(message, text_5)
                return

            self.bot.set_state(message.from_user.id, Admins.perms, message.chat.id)
            self.state_helper.save_data(message.from_user.id, message.chat.id, ['user_id'], [user_id])
            self.bot.reply_to(message, text, reply_markup=kb)
            return


    def callback_perms(self, call: types.CallbackQuery):
        data = self.get_keyboard_data(call.message.reply_markup)

        call_data = call.data.split("%")[1]
        if call_data == "accept":
            new_perms = self.perms_to_perms(data)
            user_id = self.state_helper.get_data(call.from_user.id, call.message.chat.id, ['user_id'])['user_id']
            chat_id = DataBase.get_channel_id(call.from_user.id)[0]

            try:
                user = antiflood(self.bot.get_chat_member, chat_id, user_id).user
            except:
                antiflood(self.bot.answer_callback_query,
                          callback_query_id=call.id,
                          text="Пользователя нет в канале (Либо другая ошибка)",
                          show_alert=True
                          )
                return

            try:
                antiflood(self.bot.promote_chat_member, chat_id, user_id, **new_perms)
            except:
                antiflood(self.bot.answer_callback_query,
                          callback_query_id=call.id,
                          text="Произошла какая-то ошибка",
                          show_alert=True
                          )
                return

            self.bot.delete_state(call.from_user.id, call.message.chat.id)
            DataBase.add_admin(call.message.chat.id, user)
            antiflood(self.bot.answer_callback_query,
                      callback_query_id=call.id,
                      text="Успешна 🎉",
                      show_alert=True
                      )
            return

        data[call_data] = not data[call_data]

        kb = self.generate_keyboard(data)
        antiflood(self.bot.edit_message_reply_markup, call.message.chat.id, call.message.id, reply_markup=kb)


    def generate_keyboard(self, perms: dict = None):
        kb = types.InlineKeyboardMarkup()

        if perms is None:
            perms = self.perms

        for perms_name, btn_text in self.buttons.items():
            btn_text += ": "
            if perms[perms_name]:
                btn_text += "✅"
            else:
                btn_text += "❌"

            kb.add(
                types.InlineKeyboardButton(
                    text=btn_text,
                    callback_data=f"perm%{perms_name}"
                )
            )

        kb.add(
            types.InlineKeyboardButton(
                text="-----Назначить-----",
                callback_data="perm%accept"
            )
        )

        return kb


    def get_keyboard_data(self, kb: types.InlineKeyboardMarkup):
        data = self.perms
        keyboard = kb.keyboard
        keyboard.pop()

        for button in keyboard:
            btn = button[0]
            if btn.text.endswith("✅"):
                data[btn.callback_data.split("%")[1]] = True
            else:
                data[btn.callback_data.split("%")[1]] = False

        return data


    def perms_to_perms(self, perms: dict):
        new_perms = dict()

        for perms_name, allow in perms.items():
            new_perms[self.perms_to_bot_perms[perms_name]] = allow

        return new_perms