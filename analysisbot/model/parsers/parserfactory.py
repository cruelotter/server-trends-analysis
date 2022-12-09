from analysisbot.model.parsers import *
from analysisbot.logging.logger import _logger

class ParserFactory():
    
    @staticmethod
    def create_parser(type):
        if type == "telegram":
            return ParserTelegram()
        elif type == "vk":
            return ParserVK()
        elif type == "tinkoff_journal":
            return ParserTinkoff()
        elif type == "vc_ru":
            _logger.info("[ParserFactory] feature in development")
            return None
        else:
            # raise TypeError("Parser type is not valid")
            _logger.exception("[ParserFactory] TypeError: Parser type is not valid")
            return None
