import requests
import pypyodbc
from bs4 import BeautifulSoup
import datetime
from collections import deque

#Парсим всю страницу
def get_html(url):
    r = requests.get(url)
    fi = url.split("/")
    if len(fi) > 4:
        Html_file = open(fi[2] + "region.html", "w", encoding='utf8')
    else:
        Html_file = open(fi[2]+".html", "w", encoding='utf8')
    Html_file.write(r.text)
    Html_file.close()
    return r.text

#Парсим новости
def get_toatl_str ( html):
    soup = BeautifulSoup(html, 'html.parser')
    pages = soup.find('div', class_='news').find_all('a', class_='news__tabs__item__link')
    res = {}
    for i in pages:
        res[i.text] = i.get('href')
    return res

#Записываем новости в базу данных
def write_dataBase(resultArr):
    connection = pypyodbc.connect('Driver={SQL SERVER};'
                                  'Server=DESKTOP-415KAJA\SQL2017;'
                                  'Database=TestDataBase;')
    cursor = connection.cursor()
    mySQLQuery = ("""INSERT INTO TableParser VALUES (?,?,?,?)""")
    for news in resultArr:
        if not None in news:
            cursor.execute(mySQLQuery, news)
    cursor.commit()
    connection.close()

#Парсим спорт и Новости Москвы
def get_page_news(html, _name):
    soup = BeautifulSoup(html, 'html.parser')
    headline = soup.find('div', class_='cols__wrapper').find_all('div', class_='cols__inner')
    result = []
    j = 0
    for table in headline:
        linksOfText = table.find_all('a', attrs={'class': 'link link_flex'})
        time = table.find_all('span', attrs={'class': 'newsitem__param js-ago'})
        head = table.find_all('span', attrs={'class': 'hdr__inner'})
        for i in linksOfText:
            result.append([None for i in range(0, 4)])
            result[j][0] = _name
            result[j][3] = i.text
            if "https://sportmail.ru" in i:
                result[j][1] = i.get('href')
            else:
                result[j][1] = 'https://news.mail.ru' + i.get('href')
            if(time):
                result[j][2] = datetime.datetime.strptime(time[0].get("datetime")[:-6], "%Y-%m-%dT%H:%M:%S")
            else:
                result[j][2] = datetime.date.today()
            if (head):
                result[j][0] = head[0].text
            j+=1
    write_dataBase(result)

#Парсим новости машин
def get_page_news_auto(html, _name):
    soup = BeautifulSoup(html, 'html.parser')
    headline = soup.find('div', class_='cols__wrapper').find_all('div', class_='cols__inner')
    result = []
    j = 0
    for table in headline:
        result.append([None for i in range(0, 4)])
        result[j][0] = _name
        link = table.find_all('a', attrs={'class': 'news-grid__item'})
        time = table.find_all('span', attrs={'class': 'news-grid__param js-ago'})
        text = table.find_all('span', attrs={'class': 'news-grid__title'})
        if(text):
            result[j][3] = text[0].text
        if (time):
            result[j][2] = datetime.datetime.strptime(time[0].get("datetime")[:-6], "%Y-%m-%dT%H:%M:%S")
        else:
            result[j][2] = datetime.date.today()
        if (link):
            result[j][1] = 'https://auto.mail.ru' + link[0].get("href")
        j+=1
    write_dataBase(result)

#Парсим новости женщин
def get_page_news_lady(html, _name):
    soup = BeautifulSoup(html, 'html.parser')
    headline = soup.find('div', class_='cols__wrapper').find_all('div', class_='cols__inner')
    result = []
    j = 0
    for table in headline:
        result.append([None for i in range(0,4)])
        result[j][0] = _name
        link = table.find_all('a', attrs={'class': 'newsitem__title link-holder'})
        text = table.find_all('span', attrs={'class': 'newsitem__title-inner'})
        if (text):
            result[j][3] = text[0].text
        result[j][2] = datetime.date.today()
        if (link):
            result[j][1] = 'https://lady.mail.ru/' + link[0].get("href")
        j+=1
    write_dataBase(result)

#Парсим новости hi-tech
def get_page_news_hitech(html,  _name):
    soup = BeautifulSoup(html, 'html.parser')
    headline = soup.find('div', class_='cols__wrapper').find_all('div', class_='cols__inner')
    result = []
    j = 0
    for table in headline:
        text = table.find_all('a', attrs={'class': 'list__text'})
        if (text):
            for info in text:
                result.append([None for i in range(0, 4)])
                result[j][0] = _name
                result[j][2] = datetime.date.today()
                result[j][1] = 'https://hi-tech.mail.ru/' + info.get("href")
                result[j][3] = text[0].text
                j+=1
    write_dataBase(result)

#Главная функция
def main():
    _result = get_toatl_str(get_html('https://mail.ru/'))
    for i in _result.keys():
        if _result[i] == 'https://kino.mail.ru/' or _result[i] == 'http://games.mail.ru/pc/':
            continue
        html = get_html(_result[i])
        if  'https://auto.mail.ru/' in _result[i]:
            get_page_news_auto(html, i)
        elif ('https://lady.mail.ru/' in _result[i]):
            get_page_news_lady(html, i)
        elif ('https://hi-tech.mail.ru/' in _result[i]):
            get_page_news_hitech(html, i)
        else:
            get_page_news(html, "Москва")
if __name__ == '__main__':
    main()