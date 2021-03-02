from telegram.ext import Updater, CommandHandler, Filters
from telegram import InputMediaPhoto
from logzero import logger
import logging

from queue_worker import QueueItem, MediaType

logging.basicConfig(level=logging.INFO)


class Telegram(Updater):
    def __init__(self, api_token, allowed_chat_id):
        self.api_token = api_token
        self.allowed_chat_id = allowed_chat_id
        super().__init__(self.api_token)

    def add_command_handler(self, command, handle_command_func, *args, **kwargs):
        self.dispatcher.add_handler(
            CommandHandler(command, lambda update, context: handle_command_func(*args, **kwargs),
                           filters=Filters.chat(chat_id=self.allowed_chat_id)))

    def send_media_message(self, queue_item: QueueItem):
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

            for file_path in queue_item.media:
                with open(file_path, 'rb') as photo:
                    media_group.append(InputMediaPhoto(media=photo, caption=queue_item.caption))

            self.bot.send_media_group(chat_id=self.allowed_chat_id, media=media_group, timeout=1000)
