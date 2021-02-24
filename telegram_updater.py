from telegram.ext import Updater, CommandHandler, Filters
from queue_worker import Worker
from multiprocessing import Queue


class Telegram(Updater):
    def __init__(self, config):
        self.api_token = config['ApiKey']
        self.allowed_chat_id = config['ChatId']
        self.queue = Queue()
        super().__init__(self.api_token)

    def run(self):
        queue_worker = Worker(self.queue, self.send_photo)
        queue_worker.start()

    # def add_command_handler(self, command, handle_command_func):
    #     self.dispatcher.add_handler(
    #         CommandHandler(command, handle_command_func, filters=Filters.chat(id=self.allowed_chat_id)))

    def send_photo(self, photo_file_path):
        with open(photo_file_path, 'rb') as photo:
            self.bot.send_photo(chat_id=self.allowed_chat_id, photo=photo)
