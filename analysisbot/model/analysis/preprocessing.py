import re
import pandas as pd
from datetime import date, datetime, time
from collections import Counter
# from string import punctuation
# import textacy
import spacy
# import nltk

from analysisbot.logging.logger import _logger
from analysisbot.database.mongodb import MongoManager


class Preprocessing:
    
    def __init__(self) -> None:
       
        self.mongodb = MongoManager.get_instance()
        self.included_tags = {"NOUN", "ADJ", "VERB"}
        self.nlp = spacy.load('ru_core_news_lg', exclude=['parser', 'ner', 'textcat'])
        stop_words = self.nlp.Defaults.stop_words
        # extend = {'год', 'новый', 'финансы', 'рассказать', 'финансовый','комментарий', 'пост', 'деньга', 'рассказывать', 'новость', 'финзож', 'например', 'привет', 'друг', 'друзья', 'дайджест'}
        # stop_words.union(extend)
        self.stop_words = stop_words.union({
            'финансы', 'рассказать', 'финансовый','комментарий', 'пост', 'деньга', 'рассказывать',
            'новость', 'финзож', 'например', 'привет', 'друг', 'друзья', 'дайджест', 'присоединяйтесь', 'подпишись',
            'бесплатный', "розыгрыши", "конкурсы", "бесплатно", "розыгрыш", "конкурс", "акция", 'марафон', 'подписывайтесь',
            'Подписывайтесь', 'загляните', 'упустите', 'вебинар', 'вебинаре', 'пропустите', 'регистрируйтесь', 'телеграм-канал', 
            'курсе', 'school', 'эфир', 'эфире', 'эфиру', 'приглашаем', 'ссылке', 'залетай', 'руб.'})
    
    
    # def word_to_id(self, word: str, date: datetime, ref, path):
    def word_to_id(self, word: str, segment_id):
        '''Записывает слово в словарь, возвращает id слова'''
        doc = MongoManager.find_data('dictionary', {'word': word})
        if doc is None:
            c = MongoManager.count('dictionary')
            res =  MongoManager.insert_data('dictionary', {'_id': c, 'word': word})
        else: res: int =  doc['_id']
        
        doc_segment = MongoManager.find_data(f'{segment_id}', {'_id' : res})
        if doc_segment is None:
            res =  MongoManager.insert_data(f'{segment_id}', {'_id': c, 'word': word})
        # MongoManager.insert_data('token_ref', {'token': res, 'year': date.year, 'month': date.month, 'path': path, 'ref': ref})
        return res
    
    
    def remove_emoji(self, string):
        '''Удаляет из текста эмодзи'''
        emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', string)
    
    
    def lemmatizer(self, text: str, segment_id):
        """lemmatizer
        Предобработка текста: нижний регистр, фильтр частей речи, пунктуации и стопслов, лемматизация 

        Args:
            text (str): исходный текст поста

        Returns:
            Counter: Пары вида (id слова, его частота в этом тексте)
        """        
        text = self.remove_emoji(text)
        doc = self.nlp(text.lower())
        filtered_list = []
        for token in doc:
            if (not token.is_stop) and (not token.is_punct) and (token.pos_ in self.included_tags) \
            and (not token.is_digit) and (not any([char.isdigit() for char in token.text])) and (len(token.text)>2):
                lemma = token.lemma_
                if not (lemma in self.stop_words):
                    lemma_id = self.word_to_id(lemma, segment_id)
                    filtered_list.append(str(lemma_id))
        del doc
        counter = Counter(filtered_list)
        # bigrams = list(nltk.ngrams(filtered_list, 2))
        # bigram_pairs = [("_".join([str(a[0]), str(a[1])]), counter[a[0]]+counter[a[1]]) for idx, a in enumerate(bigrams)]
        # bigram_pairs = [("_".join([str(a[0]), str(a[1]), str(b[0]), str(b[1])]), counter[a[0]]+counter[a[1]]+counter[b[0]]+counter[b[1]]) for idx, a in enumerate(bigrams) for b in bigrams[idx+2:]]
        # del bigrams
        # return dict(bigram_pairs)
        return counter
    

    def raw_to_stats(self, raw_data, path, segment_id):
        """raw_to_stats
        Данные после лемматизации собираются в таблицу с колонками 'token', 'date', 'frequency', 'views', 'reactions'

        Args:
            raw_data (List[dict]): Исходные данные постов в виде списка словарей, где каждый словарь имеет вид: 
                {'ref' : id поста,
                'text' : txt,
                'date' : дата публикации,
                'views' : кол-во просмотров,
                'reactions': кол-во реакций + коммпнтариев}
            path (_type_): путь до файла с исходниками

        Returns:
            pd.DataFrame: предобработанные данные
        """        
        cols=['token', 'date', 'frequency', 'views', 'reactions']
        data = pd.DataFrame(columns=cols)
        for i, df in enumerate(raw_data):
            # df = raw_data[i]
            date = datetime.combine(df['date'], time(0,0))
            freq_dict = self.lemmatizer(df['text'], segment_id)
            list_df = []
            for token in freq_dict:
                pd.DataFrame({'token': token, 'year': date.year, 'month': date.month, 'path': path, 'ref': str(df['ref'])}, [token]).to_csv(f'./storage/ref.csv', mode='a', index=False, header=False)
                
                list_df.append({'token' : token,
                                'date' : date,
                                'frequency' : freq_dict[token],
                                'views' : df['views'],
                                'reactions' : df['reactions']}
                               )
            new_df = pd.DataFrame(list_df, columns=cols)
            if i == 0:
                data = new_df
            else:
                data = pd.concat([data, new_df], ignore_index=True).groupby(['token', 'date']).sum(['frequency', 'views', 'reactions'])
                data.reset_index(inplace=True)
                if i % 100 == 0:
                    _logger.warning(f"{i} texts")
            del new_df
            
        _logger.warning(f"{path} {len(data.index)} preprocessing done")
        data = data.fillna(0)
        return data