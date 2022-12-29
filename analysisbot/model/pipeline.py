import pandas as pd
import numpy as np
import pathlib
import json
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
                    # _logger.error(cur)
                    try:
                        if cur is None:
                            parse_queue[src_type][source].append(start)
                            _logger.error(f"{start} | {cur}")
                            # MongoManager.insert_data(
                            # 'processed_data',
                            # {"type": src_type, "source": source, "year": start.year, "month": start.month, "full": datetime.now().isoformat()}
                        # )
                        elif datetime.combine(start, time(0,0)) >= cur["full"] or cur["full"] < datetime.combine(datetime.now().date(), time(0,0)):
                            parse_queue[src_type][source].append(start)
                            _logger.error(f"{cur['full']} | {datetime.combine(datetime.now().date(), time(0,0))}")

                    except Exception as e:
                        if datetime.combine(start, time(0,0)) >= datetime.fromisoformat(cur["full"]) or datetime.fromisoformat(cur["full"]) < datetime.combine(datetime.now().date(), time(0,0)):
                            parse_queue[src_type][source].append(start)
                            _logger.error(f"{cur['full']} | {datetime.combine(datetime.now().date(), time(0,0))}")

                        # parse_queue[src_type].append((path,[source, start, start + relativedelta(months=1)]))

                    start += relativedelta(months=1)
                    
        return parse_queue, process_queue
    
    
    def parse_preprocess_data(self, parse_queue: dict):
        # factory = ParserFactory()
        for type in parse_queue.keys():
            parser = ParserFactory.create_parser(type)
            for source in parse_queue[type].keys():
                # try:
                print(source)
                print(parse_queue[type][source])
                # os.makedirs(path[:-3], exist_ok=True)
                if parse_queue[type][source] == []:
                    _logger.warning('Nothing to parse')
                else:
                    print(parse_queue[type][source])
                    seg_type = self.seg_type
                    success = parser.get_source_data(source, parse_queue[type][source], seg_type)
                    _logger.info(success)
                    
                # except Exception as e:
                #     _logger.error(f'skipped {source}')
                #     _logger.error(e)
        
    
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
        
        preview_list = "".join([f'<li>{s}</li>' for s in top['word'].tolist()]) 
        preview = '<div><p>Выявленные тренды:</p><ol>{}</ol></div>'.format(preview_list)

        body = ""
        # p_unique = set()
        for row in top.itertuples():
            print(f'page: {row[0]} {row[1]}')()
            
            with open(f'storage/usage/usage_{row[0]}.json', 'r', encoding='utf-8') as file:
                use = json.load(file)
            print("usage found:", len(use))
            if len(use)>3: use = use[:2]
            html_examples=""
            for use_post in use:
                if use_post is None:
                    _logger.error("empty use_post")
                else:
                    try:
                        _logger.info(use_post.keys())
                        html_examples += f"<h3>{use_post['path'][15:-8]}</h3><p>{use_post['date'][:-13]}</p><p>{use_post['text']}</p>"
                    except:
                        _logger.error("keyerror 'path'")
                
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
        top, bigrams = TrendDetection.get_top_data(self.source_list, process_queue, self.history_duration, self.trend_window, 15, self.seg_type)
        pdf = self.create_html(top)
        # UserManager.set_status(self.user_id, 0)
        
        return pdf, top, bigrams
    
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
    