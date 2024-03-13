import logging

# ANSI escape sequences for some colors
COLORS = {
    'WARNING': '\033[93m',  # Yellow
    'INFO': '\033[92m',  # Green
    'DEBUG': '\033[94m',  # Blue
    'CRITICAL': '\033[95m',  # Purple
    'ERROR': '\033[91m',  # Red
    'ENDC': '\033[0m',  # Reset to default
}


class ColorFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        message = logging.Formatter.format(self, record)
        if levelname in COLORS:
            message = COLORS[levelname] + message + COLORS['ENDC']
        return message


class LoggerManager:
    def __init__(self, logger_name='root'):
        self.logger = logging.getLogger(logger_name)
        handler = logging.StreamHandler()
        for handler in self.logger.handlers[:]:  # 获取现有的处理器列表的副本
            self.logger.removeHandler(handler)  # 移除这些处理器
        handler.setFormatter(ColorFormatter('%(levelname)s: %(message)s'))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def get_logger(self):
        self.logger.propagate = False
        return self.logger
