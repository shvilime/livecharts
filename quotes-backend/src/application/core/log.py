import os
import logging
import traceback

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"
COLORS = {
    'WARNING': YELLOW,
    'INFO': WHITE,
    'DEBUG': BLUE,
    'CRITICAL': YELLOW,
    'ERROR': RED
}


class ExtraInfoFilter(logging.Filter):
    """
    Фильтр для добавления дополнительной информации в логи

    """

    def __init__(self, **kwargs):
        super(ExtraInfoFilter, self).__init__()
        for key, value in kwargs.items():
            self.__dict__.update({key: value()}) if callable(value) else self.__dict__.update({key: value})

    def filter(self, record):
        for key, value in vars(self).items():
            if value:
                record.__setattr__(key, value)
        return True


class ColoredFormatter(logging.Formatter):
    """
    Цветной форматтер

    """

    def __init__(self, fmt=None, datefmt=None, style='%', use_color=True):
        super(ColoredFormatter, self).__init__(fmt, datefmt, style)
        self.use_color = use_color

    def format(self, record):
        if self.use_color and record.levelname in COLORS:
            record.levelname = COLOR_SEQ % (30 + COLORS[record.levelname]) + record.levelname + RESET_SEQ

        if record.exc_info:
            exc_type, exc_value, exc_traceback = record.exc_info
            list_tb: list = traceback.extract_tb(exc_traceback)
            # Пробежимся по списку файлов, укоротим имена и очистим от трейсбека PEX bootstrap
            clear_list_tb: list = []
            for tb in list_tb:
                if tb.filename.startswith(".bootstrap"):
                    continue
                tb.filename = os.path.join(*tb.filename.split("/")[-2:])
                clear_list_tb.append(tb)

            record.exc_text = "".join(
                traceback.format_list(clear_list_tb) + traceback.format_exception_only(exc_type, exc_value)
            )

        return logging.Formatter.format(self, record)
