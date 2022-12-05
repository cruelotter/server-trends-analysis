from myapp.model.parsers import *
from myapp.logging.logger import _logger

class ParserFactory():
    
    @staticmethod
    def create_parser(type):
        match(type):
            case "telegram":
                return ParserTelegram()
            case "vk":
                return ParserVK()
            case "tinkoff_journal":
                return ParserTinkoff()
            case "vc_ru":
                _logger.info("[ParserFactory] feature in development")
                return None
            case _:
                # raise TypeError("Parser type is not valid")
                _logger.exception("[ParserFactory] TypeError: Parser type is not valid")
                return None
