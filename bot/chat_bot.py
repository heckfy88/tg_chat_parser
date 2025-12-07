import os

from dotenv import load_dotenv
from telegram.ext import Application, MessageHandler, filters, CommandHandler

from bot.handlers.command_handler import BotCommandHandler
from bot.handlers.message_handler import JsonMessageHandler

load_dotenv()


class ChatBot:
    __token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    __application: Application

    def __init__(self):
        if self.__token == '':
            raise Exception("Bot Token is not set")
        self.__application = Application.builder().token(self.__token).build()
        self.command_handler = BotCommandHandler()
        self.message_handler = JsonMessageHandler()

    def setup(self):
        self.__application.add_handler(
            MessageHandler(filters.Document.FileExtension("json"), self.message_handler.handle_file)
        )
        self.__application.add_handler(CommandHandler("start", self.command_handler.start))
        self.__application.add_handler(CommandHandler("process", self.command_handler.process))

    def start_app(self):
        self.__application.run_polling()