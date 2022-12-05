import toml
import re
import asyncio
import pickle
from datetime import datetime, date
from pyrogram import Client
from pyrogram.types import MessageReactions, Reaction, Message

from myapp.logging.logger import _logger
from myapp.model.parsers.parser import Parser


class ParserTelegram(Parser):
    
    def __init__(self) -> None:
        self.type = "telegram"
        config = toml.load('config.toml')['telegram-parser']
        self._api_id = config['api_id']
        self._api_hash = config['api_hash']
        self._phone = config['phone']
        self.session = Client(name = 'myparser',
                          api_id=self._api_id,
                          api_hash=self._api_hash,
                          phone_number=self._phone)
        
    async def start(self):
        await self.session.start()
        
    async def stop(self):
        await self.session.stop()
        
    
    
    def remove_emoji(self, string):
        emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', string)    
    
    
    def reaction_count(self, reactions: MessageReactions) -> int:
        if reactions is None:
            return float(0)
        count = 0
        for r in reactions.reactions:
            count += r.count
        return count
        
    
    async def get_history(self, chat_name: str, queue) -> bool:
        # session = self.session
        # await session.start()
        res = True
        stopwords = {'присоединяйтесь', 'подпишись', "бесплатный", "розыгрыши", "конкурсы", "бесплатно", "розыгрыш", "конкурс", "акция", 
                     'марафон', 'подписывайтесь', 'Подписывайтесь', 'загляните', 'упустите', 'вебинар', 'вебинаре', 'пропустите',
                     'регистрируйтесь', 'телеграм-канал', 'курсе', 'school', 'эфир', 'эфире', 'эфиру', 'приглашаем', 'ссылке', 'залетай'}
        data = []
        print(queue)
        current_month = queue[-1]
        try: 
            async for msg in self.session.get_chat_history(chat_id=chat_name):
                msg: Message
                msg_date: date = msg.date.date()
                
                c = msg_date.replace(day=1)
                if current_month != c:
                    self.save_and_clear(data, chat_name, current_month)
                    current_month = msg_date.replace(day=1)
                
                if current_month in queue:
                    # print('yes')
                    if msg.service is None:
                        txt = ''.join(filter(None, [msg.text, msg.caption]))
                        txt = self.remove_emoji(txt)
                        if any([bool(stop in txt.lower()) for stop in stopwords]):
                            continue
                        elif txt != '':
                            data.append({
                                'ref' : str(msg.id),
                                'text' : txt,
                                'date' : msg_date,
                                'views' : msg.views,
                                'reactions' : self.reaction_count(msg.reactions)
                                })
                elif (msg_date < queue[0]):
                    self.save_and_clear(data, chat_name, current_month)
                    _logger.warning(f"{chat_name} parsed")
                    break
            res = True
            print(res)
        except:
            _logger.error(f"Could not access t.me/{chat_name}")
            # await self.session.stop()
            res = False
        
        # await session.stop()
        print("session stopped")
        return res
    
    
    async def temp(self, chat_name: str, queue):
        await self.start()
        res = await self.get_history(chat_name, queue)
        await self.stop()
        # task = asyncio.create_task(self.get_history(chat_name, queue))
        # res = False
        # res = await task
        
        # try:
        #     res = await task
        # except Exception as e:
        #     print(e)
            # await self.session.stop()
        return res
    
       
    def get_source_data(self, chat_name: str, queue) -> bool:
        
        _logger.warning(f"{chat_name}")
        # data = self.get_history(session, chat_name, start, end)
        # data = session.run(self.get_history(session, chat_name, start, end))
        # res = asyncio.run(self.temp(chat_name, queue))
        res = asyncio.get_event_loop().run_until_complete(self.temp(chat_name, queue))
        return res
    
if __name__=="__main__":
    p = ParserTelegram()
    data = p.get_source_data("FinZoZhExpert", [date(2022, 10, 1), date(2022, 11, 1)])
    print(len(data))
    # print(data)