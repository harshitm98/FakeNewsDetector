import requests
import html
import time
from selenium import webdriver
import random
import urllib3
import csv

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}

data = []
proxy_list = []


def load_proxies():
    print("Loading the proxies...")
    proxy_url = "https://free-proxy-list.net/"
    driver = webdriver.PhantomJS()
    driver.set_window_size(1120, 550)
    driver.get(proxy_url)
    driver.find_element_by_xpath("/html/body/section[1]/div/div[2]/div/div[1]/div[2]/div/label/input").send_keys(
        "India")
    driver.find_element_by_xpath("/html/body/section[1]/div/div[2]/div/div[2]/div/table/thead/tr/th[5]").click()
    scrapper_count = 0
    while True:
        scrapper_count += 1
        try:
            ip_xpath = "/html/body/section[1]/div/div[2]/div/div[2]/div/table/tbody/tr[" + str(
                scrapper_count) + "]/td[1]"
            port_xpath = "/html/body/section[1]/div/div[2]/div/div[2]/div/table/tbody/tr[" + str(
                scrapper_count) + "]/td[2]"
            country_code_xpath = "/html/body/section[1]/div/div[2]/div/div[2]/div/table/tbody/tr[" + str(
                scrapper_count) + "]/td[3]"
            proxy_type_xpath = "/html/body/section[1]/div/div[2]/div/div[2]/div/table/tbody/tr[" + str(
                scrapper_count) + "]/td[5]"
            ip = driver.find_element_by_xpath(ip_xpath).text
            port = driver.find_element_by_xpath(port_xpath).text
            country_code = driver.find_element_by_xpath(country_code_xpath).text
            proxy_type = driver.find_element_by_xpath(proxy_type_xpath).text
            if proxy_type == "elite proxy" and country_code == "IN":
                proxy_list.append([ip, port])
        except Exception:
            break


def choose_proxies():
    if len(proxy_list) == 0:
        load_proxies()
    proxy = random.choice(proxy_list)
    final_proxy = proxy[0] + ":" + proxy[1]
    proxy_dict = {
        "http": final_proxy,
        "https": final_proxy
    }
    return proxy_dict


def load_news(news_id):
    proxy_dict = choose_proxies()
    payload = {
        'category': '',
        'news_offset': news_id
    }
    post_url = "https://inshorts.com/en/ajax/more_news"
    try:
        news = requests.post(post_url, payload, proxies=proxy_dict).json()
    except urllib3.exceptions.MaxRetryError:
        print("Max retry error. Connecting again to the proxy...")
        return 0
    return news


def content_sorter(html_data, news_id):
    html_data = html_data[html_data.find('<div class="news-card z-depth-1"') + 10:]

    while True:
        headline = html_data[html_data.find('itemprop="headline"') + len('itemprop="headline"') + 1:
                             html_data.find("</span>",
                                            html_data.find('itemprop="headline"') + len('itemprop="headline"'))]
        article_body = html_data[html_data.find('itemprop="articleBody">') + len('itemprop="articleBody">'):
                                 html_data.find('</div>', html_data.find('itemprop="articleBody">')
                                                + len('itemprop="articleBody">'))]
        date = html_data[html_data.find('<span class="date">') + len('<span class="date">'):
                         html_data.find('</span>', html_data.find('<span class="date">') + len('<span class="date">'))]
        source = html_data[html_data.find('href="', html_data.find('<div class="read-more">')) + len('href="'):
                           html_data.find('">', html_data.find('href="', html_data.find('<div class="read-more">'))
                                          + len('href="'))]
        data.append([news_id, date, headline, article_body, source])
        with open('news.csv', 'a+') as file:
            content_to_write = [[html.unescape(news_id), html.unescape(date), html.unescape(headline),
                                 html.unescape(article_body), html.unescape(source)]]
            writer = csv.writer(file)
            writer.writerows(content_to_write)
        if html_data.find('<div class="news-card z-depth-1"') == -1:
            break
        html_data = html_data[html_data.find('<div class="news-card z-depth-1"') + 10:]


try:
    with open('news.txt', 'r') as file:
        existing_news_data = file.read()
        existing_news_data = existing_news_data.split('\n')
        min_news_id = existing_news_data[-2]
        min_news_id = min_news_id.split('\t')[0]

except FileNotFoundError:
    url = "https://inshorts.com/en/read"
    session = requests.Session()
    result = session.get(url)
    html_code = result.text
    min_news_id = html_code[
                  html_code.find("min_news_id") + 15: html_code.find("\"", html_code.find("min_news_id") + 16)]

count = 1
while count < 10:
    print("Loading the news for the {} time...".format(count))
    json_news = load_news(min_news_id)
    while True:
        if json_news == 0:
            json_news = load_news(min_news_id)
        else:
            break
    html = json_news["html"]
    min_news_id = json_news["min_news_id"]
    content_sorter(html, min_news_id)
    time.sleep(5)
    count += 1


