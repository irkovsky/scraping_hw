import requests
from bs4 import BeautifulSoup
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep
import re


KEYWORDS = ['дизайн', 'фото', 'web', 'python']
HABR_URL = 'https://habr.com/ru/articles/'


def return_rss_url(url):
    '''Получаем адрес rss-фида'''
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    rss_url = soup.find('link', attrs={'rel': 'alternate', 'type': 'application/rss+xml'}).get('href')
    return rss_url


def parse_rss(rss_url):
    '''Формируем список данных сниппетов статей из rss-фида'''
    xml_data = requests.get(rss_url).text
    xml_soup = BeautifulSoup(xml_data, 'xml')
    all_items = xml_soup.find_all('item')[:20]
    
    articles_data = []
    
    for item in all_items:
        pubdate = item.find('pubDate').text
        title = item.find('title').text
        description = item.find('pubDate').text
        
        guid_tag = item.find('guid')
        link_tag = item.find('link')
        link = 'N/A'
        
        if guid_tag and guid_tag.text:
            link = guid_tag.text
        elif link_tag and link_tag.text:
            full_link = link_tag.text
            link = full_link.split('?')[0]
            
        pattern = r'/articles/(\d+)/'
        match = re.search(pattern, link)
        
        if match:
            art_id = match.group(1)
        else:
            art_id = 'N/A'
            
        articles_data.append([pubdate, title, description, link, art_id])
        
    return articles_data


def filter_articles(articles_data, keywords):
    '''Фильтр статей по ключевым словам на основе сниппетов'''
    result = []  
    
    for article in articles_data:
        pubdate, title, description = article[0], article[1], article[2]
        
        for key in keywords:
            pattern = r'\b' + key + r'\b'
            match_title = re.search(pattern, title, re.IGNORECASE) 
            match_description = re.search(pattern, description, re.IGNORECASE) 
            
            if match_title or match_description:
                result.append(article)
                break
            
    return result


def filter_articles_by_full_text(articles_data, keywords):
    '''Фильр статей по ключевым словам на основе полного текста статей'''
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
     
    result = dict()
     
    for article in articles_data[:3]:
         link = article[3]
         driver.get(link)
         
         sleep(5)
         
         article_body_selector = '.article-formatted-body'
         article_element = driver.find_element(By.CSS_SELECTOR, article_body_selector)
         full_text = article_element.text
         
         for key in keywords:
             pattern = r'\b' + key + r'\b'
             match = re.search(pattern, full_text, re.IGNORECASE)
             
             if match:
                 result[key] = article
                 break
     
    return result


def main():
    rss_url = return_rss_url(HABR_URL)
    print(rss_url)
    
    articles_data = parse_rss(rss_url)
    print(f'Найдено статей: {len(articles_data)}')
    
    result1 = filter_articles(articles_data, KEYWORDS)
    print('ПОИСК ПО СНИППЕТАМ ---')
    print(f'Отфильтровано статей: {len(result1)}')
    print(result1)
    
    result2 = filter_articles_by_full_text(articles_data, KEYWORDS)
    print('ПОИСК ПО ТЕКСТУ ---')
    print(f'Отфильтровано статей: {len(result2)}')
    print(result2)
    

if __name__ == '__main__':
    main()


## добавить requirements.txt 
## и сделать доп задание