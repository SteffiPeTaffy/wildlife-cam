from configparser import ConfigParser


class ConfigValidationException(Exception):
    pass


class WildlifeCamConfig(ConfigParser):
    def __init__(self, config_file):
        super(WildlifeCamConfig, self).__init__()

        self.read(config_file)
        self.validate_config()

    def validate_config(self):
        if not self.has_section('General'):
            raise ConfigValidationException('Missing required "General" section in config file')

        if not self.has_option('General', 'PhotoDirPath'):
            raise ConfigValidationException(
                'Missing required option "PhotoDirPath" in "General" section in config file')

        if not self.has_option('General', 'LogDirPath'):
            raise ConfigValidationException(
                'Missing required option "LogDirPath" in "General" section in config file')

        if not self.has_section('PirSensor'):
            raise ConfigValidationException('Missing required "PirSensor" section in config file')

        if not self.has_option('PirSensor', 'Pin'):
            raise ConfigValidationException(
                'Missing required option "LogDirPath" in "General" section in config file')

        if self.has_section('Telegram'):
            if not self.has_option('telegram', 'ApiKey'):
                raise ConfigValidationException(
                    'Missing required option "ApiKey" in "Telegram" section in config file')
            if not self.has_option('telegram', 'ChatId'):
                raise ConfigValidationException(
                    'Missing required option "ChatId" in "Telegram" section in config file')

        if self.has_section('SFTP'):
            if not self.has_option('SFTP', 'IpAddress'):
                raise ConfigValidationException(
                    'Missing required option "IpAddress" in "SFTP" section in config file')
            if not self.has_option('SFTP', 'Port'):
                raise ConfigValidationException(
                    'Missing required option "Port" in "SFTP" section in config file')
            if not self.has_option('SFTP', 'Username'):
                raise ConfigValidationException(
                    'Missing required option "Username" in "SFTP" section in config file')
            if not self.has_option('SFTP', 'Password'):
                raise ConfigValidationException(
                    'Missing required option "Password" in "SFTP" section in config file')
            if not self.has_option('SFTP', 'Directory'):
                raise ConfigValidationException(
                    'Missing required option "Directory" in "SFTP" section in config file')
