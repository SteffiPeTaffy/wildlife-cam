#!/usr/bin/python3

import pysftp
import os
from logzero import logger

from app.queue_worker import QueueItem


class Uploader:
    def __init__(self, sftp_host, sftp_port, sftp_username, sftp_password, sftp_dir):
        self.sftp_host = sftp_host
        self.sftp_port = sftp_port
        self.sftp_username = sftp_username
        self.sftp_password = sftp_password
        self.sftp_dir = sftp_dir

    def upload(self, queue_item: QueueItem):
        logger.info("wildlife-cam: Uploading photo to FTP Server")

        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        with pysftp.Connection(host=self.sftp_host, port=self.sftp_port, username=self.sftp_username,
                               password=self.sftp_password, cnopts=cnopts) as srv:

            for file_path in queue_item.media:
                self.__upload(file_path, srv)

        srv.close()

    def __upload(self, file_path, srv):
        base_path, file_name = os.path.split(file_path)
        _, sub_folder_name = os.path.split(base_path)
        try:
            with srv.cd(self.sftp_dir):
                if not srv.exists(sub_folder_name):
                    srv.mkdir(sub_folder_name)
                with srv.cd(sub_folder_name):
                    srv.put(file_path)
        except Exception as e:
            logger.info("wildlife-cam: Failed to uploaded file")
            logger.exception(e)
