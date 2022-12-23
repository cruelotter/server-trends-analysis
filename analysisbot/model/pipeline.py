import pandas as pd
import numpy as np
import pathlib
import os
# from weasyprint import HTML, CSS
# from fpdf import FPDF
from datetime import datetime, date, timedelta, time
from dateutil.relativedelta import relativedelta
from collections import defaultdict

from analysisbot.logging.logger import _logger
from analysisbot.database.mongodb import MongoManager
from analysisbot.bot.user import UserManager
from analysisbot.model.parsers.parserfactory import ParserFactory
from analysisbot.model.analysis.preprocessing import Preprocessing
from analysisbot.model.analysis.trend_detection import TrendDetection

 
class Pipeline:
    
    history_end: date
    history_start: date
    trend_window: int
    source_list: dict
    db = MongoManager.get_instance()
    preprocessing = Preprocessing()
    detection = TrendDetection()
    
    @staticmethod
    def check_source_list(source_list: str):
        typed_source_list = defaultdict(list)
        for link in source_list.split():
            try:
                if "t.me/" in link:
                    source = link.partition("t.me/")[2]
                    type = "telegram"
                elif "vk" in link:
                    source = link.partition("vk.com/")[2]
                    type = "vk"
                elif "tinkoff" in link:
                    source = link.partition("https://journal.tinkoff.ru/flows/")[2][:-1]
                    type = "tinkoff_journal"
                elif "vc.ru" in link:
                    source = link
                    type = "vc_ru"
                typed_source_list[type].append(source)
            except:
                _logger.info(f"[Pipeline] Wrong format: couldn't parse source: {link}")
            
        return typed_source_list
        
    
    def __init__(self, user_id, history_duration: int, trend_window: int, source_list: str, seg_type) -> None:
        self.user_id = user_id
        self.history_duration = history_duration
        self.history_end = datetime.today().date()
        self.history_start = (self.history_end - timedelta(days=history_duration*30)).replace(day=1)
        self.trend_window = trend_window
        self.source_list = self.check_source_list(source_list)
        self.seg_type = seg_type
        
        
    def check_existance(self):
        parse_queue = defaultdict(dict)
        process_queue = []
        for src_type in self.source_list.keys():
            for source in self.source_list[src_type]:
                parse_queue[src_type][source] = []
                end = self.history_end
                start = self.history_start
                while start <= end:
                    path = "./storage/data/{}/{}/{}/{}".format(src_type, source, str(start.year), str(start.month).zfill(2))
                    process_queue.append(path)
                    cur = MongoManager.find_data(
                        'processed_data',
                        {"type": src_type, "source": source, "year": start.year, "month": start.month}
                        )
                    try:
                        if cur is None:
                            parse_queue[src_type][source].append(start)
                            # MongoManager.insert_data(
                            # 'processed_data',
                            # {"type": src_type, "source": source, "year": start.year, "month": start.month, "full": datetime.now().isoformat()}
                        # )
                        elif cur["full"] >= datetime.combine(datetime.now().date(), time(0,0)):
                            parse_queue[src_type][source].append(start)
                    except:
                        if datetime.fromisoformat(cur["full"]) >= datetime.combine(datetime.now().date(), time(0,0)):
                            parse_queue[src_type][source].append(start)
                        # parse_queue[src_type].append((path,[source, start, start + relativedelta(months=1)]))

                    start += relativedelta(months=1)
                    
        return parse_queue, process_queue
    
    
    def parse_preprocess_data(self, parse_queue: dict):
        # factory = ParserFactory()
        for type in parse_queue.keys():
            parser = ParserFactory.create_parser(type)
            for source in parse_queue[type].keys():
                try:
                    print(source)
                    print(parse_queue[type][source])
                    # os.makedirs(path[:-3], exist_ok=True)
                    if parse_queue[type][source] == []:
                        _logger.warning('Nothing to parse')
                    else:
                        print(parse_queue[type][source])
                        success = parser.get_source_data(source, parse_queue[type][source])
                        _logger.info(success)
                    
                except Exception as e:
                    _logger.error(f'skipped {source}')
                    _logger.error(e)

    '''    
    def read_pkl(self, path, ref):
        l_raw = pd.read_pickle(path+'raw.pkl')
        # print(l_raw)
        raw = pd.DataFrame(l_raw)
        # print(raw.head(3).to_string())
        if l_raw == []:
            _logger.warning('Empty source file')
            return []
        else:
            found = raw.loc[raw['ref']==ref]
            return found['text'].to_numpy()
    
    def usage2(self, token, p_unique):
        # MongoManager.insert_data('token_ref', {'token': res, 'year': date.year, 'month': date.month, 'path': path, 'ref': ref})
        date = datetime.today()
        contains = set()
        ref_tok = [set(), set()]
        for idx, word in enumerate(token.split('_')):
            doc: list = MongoManager.find_data('token_ref', {'token': int(word), 'year': date.year, 'month': date.month}, multiple=True)
            # print(doc)
            for d in doc:
                try:
                    contains.add((d['ref'], d['path']))
                    ref_tok[idx].add(d['ref'])
                except Exception as e:
                    _logger.error("Could not add ref doc")
                    print(e)
            
        ref_set = ref_tok[0].intersection(ref_tok[1], ref_tok[2], ref_tok[3])
        del ref_tok
        # print(f"ref_set {len(ref_set)}")
        
        res = []
        i = 0
        for ref, path in contains:
            if (ref in ref_set) and (path[10:-8] not in p_unique) and i<4:
                text = self.read_pkl(path, ref)
                res.append([path[10:-8], text])
        del ref_set
        del contains           
        
        return res
    
    
    def usage(self, token, p_unique:set):
        date = datetime.today()
        try:
            df = pd.read_csv(f'./storage/ref.csv', dtype={'token':object, 'year':int, 'month':int, 'path':object, 'ref':object})
        except Exception as e:
            print(token, end=' __ ')
            print(e)
            return [["Not found", 'not found']]
        df = df[df['token']==token]
        docs: pd.DataFrame = df.loc[(df['year']==date.year) & (df['month']==date.month), ['path', 'ref']]
        docs.reset_index(inplace=True)
        del df
        # docs: list = MongoManager.find_random('token_ref', {'token': token, 'year': date.year, 'month': date.month})
        print(len(docs))
        if len(docs)==0:
            return [["Not found", 'not found']]
        res = []
        for i,doc in docs.iterrows():
            if i>3: return res
            if not doc['ref'] in p_unique:
                path = doc['path']
                text = self.read_pkl(path, doc['ref'])
                res.append([path[10:-8], text])
        del docs
        return res
'''               
                
        
    
    def create_html(self, top: pd.DataFrame):
        html_head = '<!DOCTYPE html><html><head><title>Report</title><style>html * {font-family: Arial, Helvetica, sans-serif;margin-left: 50px;margin-right: 50px;max-width: 1500px;}</style></head>'
        html_body = 'html<body>{}{}{}</body></html>'
        page_str = '<div><h2>{}</h2><img src="{}"/><h2>Примеры постов:</h2>{}</div>'
        # page_str = '<div><h2>{}</h2><img src="{}"/></div>'
        # post_str = '<h3>{}</h3><p>{}</p>'
        
        _logger.warning('PDF is creating')
        usr = UserManager.get_from_db(self.user_id)
        li_sources = ''
        for s in usr.sources.split():
            li_sources += f'<li>{s}</li>'
        
        path = pathlib.Path("/home/server-trends-analysis/storage/img/all.png").as_uri()
        header = '<div><h1>Отчет</h1><p>История c {} по {}</p><p>Выделять тренд за {} дня(ей)</p><p>Источники:</p><ul>{}</ul><img src="{}"/></div>'.format(self.history_start, self.history_end, self.trend_window, li_sources, path)
        
        preview_list = "".join([f'<li>{s}</li>' for s in top['word'].tolist()]) #!###############################################
        preview = '<div><p>Выявленные тренды:</p><ol>{}</ol></div>'.format(preview_list)
        
        # top_np = top.to_numpy()
        # print(top_np)
        body = ""
        # p_unique = set()
        for row in top.itertuples():
            print(f'page: {row[0]} {row[1]}')
            # use = self.usage(old[i], p_unique)
            # example_posts = ""
            # for post in use:
            #     p_unique.add(post[0])
            #     example_posts += post_str.format(post[0], post[1])
                
            # path = pathlib.Path(f"/home/cruelotter/sber/trends_analysis/storage/img/history_{old[i]}.png").as_uri()
            import json
            with open(f'storage/usage/usage_{row[0]}.json', 'r', encoding='utf-8') as file:
                use = json.load(file)
            print("usage found:", len(use))
            if len(use)>3: use = use[:2]
            html_examples=""
            for use_post in use:
                html_examples += f"<h3>{use_post['path'][15:-8]}</h3><p>{use_post['date'][:-13]}</p><p>{use_post['text']}</p>"
                
            path = pathlib.Path(f"/home/server-trends-analysis/storage/img/img_{row[0]}.png").as_uri()
            body += page_str.format(row[1], path, html_examples)
            print('ok')
        path = f"./storage/reports/report_{int(datetime.now().timestamp())}"
        
        s = html_head + html_body.format(header, preview, body)
        print(path)
        os.makedirs(f"./storage/reports", exist_ok=True)
        with open(f'{path}.html', 'w') as f:
            f.write(s)
        # html = HTML(string=s, base_url="/trends_analysis")
        print('html created')

        return path
        
                   
    ''' def create_pdf(self, top: np.ndarray, data: pd.DataFrame):
            width = 215.9
            height = 279.4
            pdf = FPDF()
            pdf.add_font('"Sans', '', 'analysisbot/model/fonts/NotoSans-Regular.ttf', uni=True)

            pdf.add_page()
            pdf.image(f"./storage/img/all.png", 0, 0, width)
            _logger.warning('PDF is creating')
            i = 0
            for token in data.columns:
                print(f'page {i}')
                pdf.add_page()
                # pdf.add_font('"Sans', '', './storage/NotoSans-Regular.ttf', uni=True)
                pdf.set_font('"Sans', '', 22)
                pdf.cell(0, 10, txt=f"{int(top[i])} - {token}", ln=1, align='C')
                # pdf.write(5, f" {int(top[i])} - {token}")
                pdf.image(f"./storage/img/history_{token}.png", 0, 0, width-20)
                use = self.usage(top[i])
                print('okk')
                pdf.set_font('"Sans', '', 16)
                pdf.write(height/2, 'Примеры постов:\n')
                for t in use:
                    pdf.cell(0, 10, txt=t[0], ln=1, align='L')
                    pdf.cell(0, 10, txt=t[1], ln=1, align='L')
                    # pdf.write(height/2+10, r'{}'.format(t[1]))
                i += 1
                print('ok')
            path = f"./storage/pdf/report_{int(datetime.now().timestamp())}.pdf"
            pdf.output(path)    
            return path
    '''
                    
    def run(self):
        # UserManager.set_status(self.user_id, 1)
        parse_queue, process_queue = self.check_existance()
        self.parse_preprocess_data(parse_queue)
        
        trend_window_end = datetime.combine(datetime.today(), time(0,0))
        trend_window_start = trend_window_end - relativedelta(days=self.trend_window*2)

        # UserManager.set_status(self.user_id, 2)
        # renamed, tok_columns = TrendDetection.get_top_data(self.source_list, process_queue, self.history_duration, self.trend_window, 15)
        top = TrendDetection.get_top_data(self.source_list, process_queue, self.history_duration, self.trend_window, 15)
        pdf = self.create_html(top)
        # UserManager.set_status(self.user_id, 0)
        
        return pdf, top
    
if __name__=="__main__":
    
    
    sources =['t.me/FinZoZhExpert', 't.me/investorbiz',]
            #   't.me/Reddit',
            #     't.me/tinkoff_invest_official', 't.me/coinkeeper', 't.me/vcnews',
            #     'vk.com/nrnews24', 'vk.com/noboring_finance',
            #     'https://journal.tinkoff.ru/flows/business-russia/', 'https://journal.tinkoff.ru/flows/crisis/',
            #     'https://journal.tinkoff.ru/flows/edu-news/', 'https://journal.tinkoff.ru/flows/opinion/',
            #     'https://journal.tinkoff.ru/flows/readers-travel/', 'https://journal.tinkoff.ru/flows/culture/', 
            #     'https://journal.tinkoff.ru/flows/hobby/']
    
    # sources = ['t.me/FinZoZhExpert', 't.me/investorbiz', 't.me/Reddit',
    #               't.me/tinkoff_invest_official', 't.me/coinkeeper', 't.me/vcnews']
    sources = " ".join(sources)
    pip = Pipeline(957739166, 3, 14, sources)
    pip.run()
    print('job finished')
    