import requests
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime, date

import time

from myapp.model.parsers.parser import Parser
from myapp.logging.logger import _logger

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ParserTinkoff(Parser):
    
    def __init__(self) -> None:
        self.type = "tinkoff_journal"
        
    def getButtons(self, driver):
        time.sleep(5)
        print('getButtons')
        try:
            branchCuts = driver.find_elements(By.XPATH, "//button[contains(@class, 'branchCut')]")
            print(len(branchCuts))
            if len(branchCuts) > 0:
                for branchCut in branchCuts:
                    branchCut.click()
                time.sleep(5)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.getButtons(driver)
        except:
            return 
    
    def getComments(self):
        url = '/discuss/overvalued-movies'
        # url = '/discuss/itogi-biznesa-2022'
        service = ChromeService(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.get(f'https://journal.tinkoff.ru{url}/')
        button = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'expandButton')]")))
        button.click()
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.getButtons(driver)
        time.sleep(5)
        # commentsWrapper = driver.find_element(By.XPATH, "//div[contains(@class, 'commentsWrap')]")
        # commentsWrapper.execute_script()
        elements = driver.find_elements(By.XPATH, "//p[contains(@class, 'text')]")
        print(len(elements))
        
        comments = []
        for el in elements:
            comments.append(el.text)
            # print(el.text)
        return " ".join(comments)

        
        
    def get_posts(self, page: BeautifulSoup, queue, chat_name):
        # news = page.find_all('a', class_="link--sKzdE")
        cards = page.find_all('div', class_=re.compile("^card--\S+"))
        headers = [c.find('div', class_=re.compile("^header--\S+")) for c in cards]
        # headers = cards.find_all('div', class_=re.compile("^header--\S+"))
        news =[h.find('a', class_=re.compile("^link--\S+")) for h in headers]

        posts = []
        current_month = queue[-1]
        for link in news:
            url = link.get('href')
            _logger.info(f'https://journal.tinkoff.ru{url}')
            r = requests.get(f'https://journal.tinkoff.ru{url}')
            try:
                post = BeautifulSoup(r.text, 'html.parser')
            
                header = post.find('div', class_='article-header__meta')
                header_meta = header.find('div', attrs={'data-component-name':'articleHeaderMeta'}).get('data-component-data')
                meta = json.loads(header_meta)
                meta_date = meta['date']
                msg_date = datetime.strptime(meta_date[:10], '%Y-%m-%d').date()
                c = msg_date.replace(day=1)
                if current_month != c:
                    # print('cur', current_month)
                    self.save_and_clear(posts, chat_name, current_month)
                    current_month = msg_date.replace(day=1)

                if current_month in queue:
                    stats = meta['stats']
                    text = []
                    content = post.find('div', class_="article-body")
                    paragraphs = content.find_all('p', {'class':'paragraph'})
                    if len(paragraphs) > 0:
                        text = []
                        headings = content.find_all('h2', class_='heading')
                        for h in headings:
                            text.append(h.get_text())
                        for p in paragraphs:
                            t: str = p.get_text()
                            text.append(t.replace("\xa0", " "))

                        post = {
                            'ref': f'https://journal.tinkoff.ru{url}',
                            'text': " ".join(text),
                            'date': msg_date,
                            'views': stats['views'],
                            'reactions': stats['comments']+stats['favoritesCount']
                        }
                        posts.append(post)
                elif msg_date < queue[0]:
                    # self.save_and_clear(data, chat_name, current_month)
                    return True, posts
                else: continue
            except:
                _logger.error(f'Fail to parse page: https://journal.tinkoff.ru{url}')
                # with open() as f:
                #     pickle.dump(post, f)  
            
        return False, posts


    def get_history(self, channel: str, queue):
        url_list = [f"/flows/{channel}"]
        data = []
        while len(url_list)>0:
            url = url_list.pop()
            _logger.info(f'https://journal.tinkoff.ru{url}/')
            r = requests.get(f'https://journal.tinkoff.ru{url}/')
            page = BeautifulSoup(r.text, 'html.parser')
            
            out_date, posts = self.get_posts(page, queue, channel)
            data.extend(posts)
            del posts
            
            if out_date:
                # nav = page.find('div', class_='paginator--dEqKc')
                nav = page.find('div', class_=re.compile("^paginator--\S+"))
                if nav is not None:
                    # next = nav.find('a', class_='next--Lf8_A')
                    next = nav.find('a', class_=re.compile("^next--\S+"))
                    if next.get("data-disabled") == "false":
                        url_list.append(next.get("href"))
                
        return data
        
    
    def get_source_data(self, chat_name: str, queue):
        _logger.warning(f"{chat_name}")
        data = self.get_history(chat_name, queue)
        _logger.warning(f"{chat_name} {len(data)} parsed")
        return data
    
    
class ParserTest():
    def __init__(self) -> None:
        self.type = "tinkoff_journal"
        
    
    def getButtons(self, driver):
        time.sleep(5)
        print('getButtons')
        try:
            branchCuts = driver.find_elements(By.XPATH, "//button[contains(@class, 'branchCut')]")
            print(len(branchCuts))
            if len(branchCuts) > 0:
                for branchCut in branchCuts:
                    branchCut.click()
                time.sleep(5)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.getButtons(driver)
        except:
            return 

    def getSite(self):
        url = '/discuss/overvalued-movies'
        # url = '/discuss/itogi-biznesa-2022'
        service = ChromeService(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.get(f'https://journal.tinkoff.ru{url}/')
        button = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'expandButton')]")))
        button.click()
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.getButtons(driver)
        time.sleep(5)
        # commentsWrapper = driver.find_element(By.XPATH, "//div[contains(@class, 'commentsWrap')]")
        # commentsWrapper.execute_script()
        elements = driver.find_elements(By.XPATH, "//p[contains(@class, 'text')]")
        print(len(elements))
        
        for el in elements: 
            print(el.text)
        # WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.CSS_SELECTOR, '''div[itemprop="comment"'''))
        
        # print(driver.title)

        # elements = driver.find_elements(By.CSS_SELECTOR, '''div[itemprop="comment"]''')

        # # page = BeautifulSoup(r.text, 'html.parser')
        
        # for el in elements:
        #     text = el.find_element(By.CSS_SELECTOR, '''p[itemprop="text"]''').get_attribute('value')
        #     print(text)


if __name__=="__main__":
    p = ParserTest()
    p.getSite()
    # s = '/workplaces/'
    # # "https://journal.tinkoff.ru/flows/crisis/"
    # # chat_name = 'noboring_finance'
    # start = datetime(2022, 11, 1).date()
    # end = datetime.now().date()
    # data = p.get_history(s, [start])
    # import pandas as pd
    # fd = pd.DataFrame(data)
    # fd.to_csv('tink.csv')
