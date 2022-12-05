from myapp.model.parsers.telegram import ParserTelegram
from myapp.model.parsers.vk import ParserVK
from myapp.model.parsers.tinkoff import ParserTinkoff
from myapp.model.parsers.parser import Parser

__all__ = ['Parser', 'ParserTelegram', 'ParserVK', 'ParserTinkoff']