from telegram.ext import Updater, CommandHandler, Filters
from telegram import InputMediaPhoto
from logzero import logger
import logging

from queue_worker import MediaItem, MediaType

logging.basicConfig(level=logging.INFO)


class Telegram(Updater):
    def __init__(self, api_token, allowed_chat_id):
        self.api_token = api_token
        self.allowed_chat_id = allowed_chat_id
        super().__init__(self.api_token)

    def add_command_handler_with_arg(self, command, handle_command_func):
        self.dispatcher.add_handler(
            CommandHandler(command,
                           lambda update, context: handle_command_func(context.args and context.args[0] or None),
                           filters=Filters.chat(chat_id=self.allowed_chat_id), pass_args=True))

    def add_command_handler(self, command, handle_command_func):
        self.dispatcher.add_handler(
            CommandHandler(command, lambda update, context: handle_command_func(),
                           filters=Filters.chat(chat_id=self.allowed_chat_id)))

    def send_message(self, message=''):
        self.bot.send_message(chat_id=self.allowed_chat_id, text=message)

    def send_media_message(self, queue_item: MediaItem):
        logger.info("wildlife-cam: Sending message to Telegram chat %s ", self.allowed_chat_id)

        if queue_item.type == MediaType.PHOTO:
            with open(queue_item.media[0], 'rb') as photo:
                self.bot.send_photo(chat_id=self.allowed_chat_id, photo=photo, caption=queue_item.caption)

        if queue_item.type == MediaType.VIDEO:
            with open(queue_item.media[0], 'rb') as video:
                self.bot.send_video(chat_id=self.allowed_chat_id, video=video, supports_streaming=True, timeout=5000,
                                    caption=queue_item.caption)

        if queue_item.type == MediaType.SERIES:
            media_group = list()

            for index, file_path in enumerate(queue_item.media):
                with open(file_path, 'rb') as photo:
                    if index == 0:
                        media_group.append(InputMediaPhoto(media=photo, caption=queue_item.caption))
                    else:
                        media_group.append(InputMediaPhoto(media=photo))

            self.bot.send_media_group(chat_id=self.allowed_chat_id, media=media_group, timeout=1000)
