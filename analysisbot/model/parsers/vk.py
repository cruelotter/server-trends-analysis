import toml
import re
import vk_api
from datetime import datetime

import analysisbot.model.parsers.parser as parser
from analysisbot.logging.logger import _logger


class ParserVK(parser.Parser):
    
    def __init__(self) -> None:
        self.type = "vk"
        config = toml.load('config.toml')['vk']
        # _app_id = config['app_id']
        _login = config['login']
        _password = config['password']
        
        self.session = vk_api.VkApi(login=_login,
                                    password=_password)
        try:
            self.session.auth(token_only=True)
        except vk_api.AuthError as e:
            _logger.exception(e)
    
    
    def get_history(self, chat_name, queue, segment_id, retry=True):
        data = []
        current_month = queue[-1]
        try:
            wall = vk_api.VkTools(self.session).get_all_iter(method='wall.get', max_count=10, values={'domain': chat_name})
            for wallpost in wall:
                try:
                    post_date = datetime.fromtimestamp(wallpost['date']).date()
                    c = post_date.replace(day=1)
                    if current_month != c:
                        # print('cur', current_month)
                        self.save_and_clear(data, chat_name, current_month, segment_id)
                        current_month = post_date.replace(day=1)
                    if current_month in queue:
                        data.append({
                            'ref': str(wallpost['id']),
                            'text': re.sub("[\[].*?[\|]", "", wallpost["text"]).replace("]", ""),
                            'date': post_date,
                            'views': wallpost["views"]["count"],
                            'reactions': wallpost["likes"]["count"] + wallpost["comments"]["count"] + wallpost["reposts"]["count"]
                            })
                    elif post_date < queue[0]:
                        _logger.info(f"[ParserVK] {chat_name} {len(data)} parsed")
                        break
                except:
                    _logger.error(f'[ParserVK] {chat_name} fail to get data')
                    break
        except Exception as e:
            if str(e) == "[29] Rate limit reached":
                _logger.error("[29] Rate limit reached")
                import time
                time.sleep(30)
                if retry:
                    data = self.get_history(self, chat_name, queue, segment_id, retry=False)
                else:
                    raise e
        return data
        
        
    def get_source_data(self, chat_name, queue, segment_id):
        _logger.warning(f"{chat_name}")
        data = self.get_history(chat_name, queue, segment_id)
        # _logger.warning(f"{chat_name} {len(data)} parsed")
        return bool(data)
    
    
# if __name__=="__main__":
#     p = ParserVK()
#     chat_name = 'noboring_finance'
#     start = datetime(2022, 11, 1)
#     end = datetime.now()
#     data = p.get_history(chat_name, start, end)
    
    