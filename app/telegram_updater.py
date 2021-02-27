from telegram.ext import Updater, CommandHandler, Filters
from logzero import logger
import logging

logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class Telegram(Updater):
    def __init__(self, api_token, allowed_chat_id):
        self.api_token = api_token
        self.allowed_chat_id = allowed_chat_id
        super().__init__(self.api_token)

    def add_command_handler(self, command, handle_command_func):
        self.dispatcher.add_handler(
            CommandHandler(command, lambda update, context: handle_command_func(),
                           filters=Filters.chat(chat_id=self.allowed_chat_id)))

    def send_photo(self, photo_file_path):
        logger.info("wildlife-cam: Sending photo to Telegram chat %s ", self.allowed_chat_id)
        with open(photo_file_path, 'rb') as photo:
            self.bot.send_photo(chat_id=self.allowed_chat_id, photo=photo)
