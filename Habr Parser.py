from bs4 import BeautifulSoup
import requests
import os
import json
import datetime
import time

start = time.clock()
os.chdir(os.path.dirname(__file__))
currentDir = os.getcwd()

HABR_START = "https://habr.com"
PAGE = "/page"

fullJson = []


def get_habr_pages():
    page_number = 1
    last_page_link = "https://habr.com/ru/flows/develop/"
    last_page_r = requests.get(last_page_link)
    last_page_soup = BeautifulSoup(last_page_r.content, features="html.parser")
    last_page_number = int(last_page_soup.find_all("div", "tm-pagination__page-group")[-1].element("a").getText())
    while page_number != last_page_number:
        page_link = HABR_START + "/ru/flows/develop" + PAGE + str(page_number) + "/"
        try:
            page_r = requests.get(page_link)
            page_soup = BeautifulSoup(page_r.content, features="html.parser")
            articles = page_soup.find_all('article')
            for article in articles:
                id = article.get('id')
                views = article.element("span", "tm-icon-counter__value").getText()
                try:
                    article_link = HABR_START + article.element('a', 'tm-article-snippet__title-link').get('href')
                    get_article_data(article_link, id, views)
                except:
                    article_link = HABR_START + article.element('div', 'tm-article-snippet').element('a', 'tm-article-snippet__readmore').get(
                        'href')
                    get_article_data(article_link, id, views)
                    pass
        except:
            pass

        print(page_number)
        page_number += 1


def get_article_data(article_link, id, views):
    dict_for_article = {"id": id}
    try:
        article_r = requests.get(article_link)
        article_soup = BeautifulSoup(article_r.content, features="html.parser")

        author = article_soup.find('a', 'tm-user-info__username')
        dict_for_article["author"] = author.getText().replace("\n", "").strip()

        article_time = article_soup.find('span', "tm-article-snippet__datetime-published").find("time").get("title")
        date = article_time.split(',')[0]
        dict_for_article["publicationTime"] = (datetime.datetime(2022, 5, 11) - datetime.datetime.strptime(date, '%Y-%m-%d')).days

        article_title = article_soup.find("h1", "tm-article-snippet__title").find("span").getText()
        dict_for_article["title"] = article_title

        article_text = article_soup.find("div", "article-formatted-body").getText()
        dict_for_article["text"] = article_text

        article_tags = []
        article_tags_text = article_soup.find_all("a", "tm-tags-list__link")
        for articleTag in article_tags_text:
            article_tags.append(articleTag.getText().strip())
        dict_for_article["tags"] = article_tags

        article_hubs = []
        article_hubs_text = article_soup.find_all("a", "tm-hubs-list__link")
        for articleHub in article_hubs_text:
            article_hubs.append(articleHub.getText().replace("\n", "").strip())
        dict_for_article["hubs"] = article_hubs

        article_rating = article_soup.find("span", "tm-votes-meter__value").getText()
        dict_for_article["rating"] = int(article_rating)
        if views[-1] == 'K':
            int_views = int(views[:-1]) * 1000
        elif views[-1] == 'M':
            int_views = int(views[:-1]) * 1000000
        else:
            int_views = int(views)
        dict_for_article["views"] = int_views

        fullJson.append(dict_for_article)
    except:
        pass


get_habr_pages()
pathForJson = currentDir + "/habr.json"
with open(pathForJson, "w", encoding='utf-8') as file:
    json.dump(fullJson, file, ensure_ascii=False, indent=4)
print("end")
