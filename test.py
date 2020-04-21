import requests
import pypyodbc
import pymysql
from bs4 import BeautifulSoup
import csv
import datetime
from collections import deque
import glob, os

#Парсим всю страницу
def get_html(url):
    page = open(url, encoding='utf8')
    soup = BeautifulSoup(page.read(), 'html.parser')
    return soup

#Записываем новости в базу данных
def write_dataBase(resultArr):
    connection = pymysql.connect('localhost', 'root', '', 'parser')
    cursor = connection.cursor()
    mySQLQuery = ("""INSERT INTO ParserMail VALUES (%s, %s, %s,%s)""")
    for news in resultArr:
        print(news)
        if not None in news:
            cursor.execute(mySQLQuery, news)
    connection.commit()
    connection.close()

#Парсим Новости Москвы
def get_page_news(soup, _name):
    headline = soup.find('div', class_='cols__wrapper').find_all('div', class_='cols__inner')
    result = []
    j = 0
    for table in headline:
        linksOfText = table.find_all('a', attrs={'class': 'link link_flex'})
        time = table.find_all('span', attrs={'class': 'newsitem__param js-ago'})
        head = table.find_all('span', attrs={'class': 'hdr__inner'})
        for i in linksOfText:
            result.append([None for i in range(0, 4)])
            result[j][0] = 'Москва'
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

#Парсим спорт
def get_page_news_sport(soup, _name):
    headline = soup.find('div', class_='cols__wrapper').find_all('div', class_='cols__inner')
    result = []
    j = 0
    for table in headline:
        linksOfText = table.find_all('a', attrs={'class': 'link link_flex'})
        time = table.find_all('span', attrs={'class': 'newsitem__param js-ago'})
        head = table.find_all('span', attrs={'class': 'hdr__inner'})
        for i in linksOfText:
            result.append([None for i in range(0, 4)])
            result[j][0] = "Спорт"
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
def get_page_news_auto(soup, _name):
    headline = soup.find('div', class_='cols__wrapper').find_all('div', class_='cols__inner')
    result = []
    j = 0
    for table in headline:
        result.append([None for i in range(0, 4)])
        result[j][0] = 'Автомобили'
        link = table.find_all('div', attrs={'class': 'p-main-news__item'})
        link = link[0].find('a')
        time = table.find_all('span', attrs={'class': 'photo__inner'})
        text = table.find_all('span', attrs={'class': 'photo__title'})
        if(link):
            result[j][3] = text[0].text
        if (time):
            result[j][2] = datetime.datetime.strptime(time[0].get("datetime")[:-6], "%Y-%m-%dT%H:%M:%S")
        else:
            result[j][2] = datetime.date.today()
        if (link):
            result[j][1] = 'https://auto.mail.ru' + link.get("href")
        j+=1
    write_dataBase(result)

#Парсим новости женщин
def get_page_news_lady(soup, _name):
    headline = soup.find('div', class_='cols__wrapper').find_all('div', class_='cols__inner')
    result = []
    j = 0
    for table in headline:
        result.append([None for i in range(0,4)])
        result[j][0] = 'Женщины'
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
def get_page_news_hitech(soup,  _name):
    headline = soup.find('div', class_='cols__wrapper').find_all('div', class_='cols__inner')
    result = []
    j = 0
    for table in headline:
        text = table.find_all('a', attrs={'class': 'list__text'})
        if (text):
            for info in text:
                result.append([None for i in range(0, 4)])
                result[j][0] = 'Hi-Tech'
                result[j][2] = datetime.date.today()
                result[j][1] = 'https://hi-tech.mail.ru/' + info.get("href")
                result[j][3] = text[0].text
                j+=1
    write_dataBase(result)

#Выбираем все html файлы в директории
def get_file():
    os.chdir(".")
    return glob.glob("*.html")


#Главная функция
def main():
    _result = get_file()
    for i in _result:
        html = get_html(i)
        if  'auto.mail.ru.html' in i :
            get_page_news_auto(html, i)
        elif ('lady.mail.ru.html' in i):
            get_page_news_lady(html, i)
        elif ('hi-tech.mail.ru.html' in i):
            get_page_news_hitech(html, i)
        elif ('sport.mail.ru' in i):
            get_page_news_sport(html, i)
        elif('news.mail.ruregion' in i):
            get_page_news(html, i)
if __name__ == '__main__':
    main()