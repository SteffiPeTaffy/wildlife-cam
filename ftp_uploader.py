import pysftp
import os
from logzero import logger


class Uploader:
    def __init__(self, config):
        self.sftp_host = config['IpAddress']
        self.sftp_port = int(config['Port'])
        self.sftp_username = config['Username']
        self.sftp_password = config['Password']
        self.sftp_dir = config['Directory']

    def upload(self, file_path):
        logger.info("wildlife-cam: Uploading photo to FTP Server")

        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        with pysftp.Connection(host=self.sftp_host, port=self.sftp_port, username=self.sftp_username,
                               password=self.sftp_password, cnopts=cnopts) as srv:

            base_path, file_name = os.path.split(file_path)
            _, sub_folder_name = os.path.split(base_path)

            try:
                srv.cd(self.sftp_dir)
                if not srv.exists(sub_folder_name):
                    srv.mkdir(sub_folder_name)
                srv.cd(sub_folder_name)
                srv.put(file_path, file_name)
            except Exception as e:
                logger.info("wildlife-cam: Failed to uploaded file")
                logger.exception(e)

        srv.close()
