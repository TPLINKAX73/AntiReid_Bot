import telebot
import sqlite3

from modules import *
from files import config
from telebot.custom_filters import StateFilter
from telebot.storage import StateMemoryStorage


# WEBHOOK_HOST = 'localhost'
# WEBHOOK_PORT = 443
# WEBHOOK_LISTEN = '0.0.0.0'
#
# WEBHOOK_SSL_CERT = 'webhook/webhook_cert.pem'
# WEBHOOK_SSL_PRIV = 'webhook/webhook_pkey.pem'
#
# WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
# WEBHOOK_URL_PATH = "/%s/" % config.token_bot
#
# class WebhookServer(object):
#     @cherrypy.expose
#     def index(self):
#         if 'content-length' in cherrypy.request.headers and \
#                         'content-type' in cherrypy.request.headers and \
#                         cherrypy.request.headers['content-type'] == 'application/json':
#             length = int(cherrypy.request.headers['content-length'])
#             json_string = cherrypy.request.body.read(length).decode("utf-8")
#             update = telebot.types.Update.de_json(json_string)
#
#             bot.process_new_updates([update])
#             return ''
#         else:
#             raise cherrypy.HTTPError(403)


DataBase()
state_storage = StateMemoryStorage()

bot = telebot.TeleBot(config.token_bot, parse_mode="html", skip_pending=True, disable_web_page_preview=True, state_storage=state_storage)


BotMenu(bot)
Backend(bot)
AntiReidBotAdd(bot)
BotAdmins(bot)


# bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH, certificate=open(WEBHOOK_SSL_CERT, 'r'), drop_pending_updates=True)
#
# cherrypy.config.update({
#     'server.socket_host': WEBHOOK_LISTEN,
#     'server.socket_port': WEBHOOK_PORT,
#     'server.ssl_module': 'builtin',
#     'server.ssl_certificate': WEBHOOK_SSL_CERT,
#     'server.ssl_private_key': WEBHOOK_SSL_PRIV
# })
#
# cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})

bot.add_custom_filter(StateFilter(bot))
bot.polling(allowed_updates=['message', 'edited_message', 'channel_post', 'edited_channel_post', 'callback_query', 'my_chat_member', 'chat_member', 'chat_join_request'])