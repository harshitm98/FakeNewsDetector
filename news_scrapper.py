import requests
import time
import csv

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}

data = []


def load_proxies():
    proxy_url = "https://api.getproxylist.com/proxy"
    proxy_session = requests.Session()
    proxy_result = proxy_session.get(proxy_url).json()
    return proxy_result['ip'], proxy_result['port']


def load_news(news_id):
    ip, port = load_proxies()
    proxy = str(ip) + ":" + str(port)
    proxy_dict = {
        "http": proxy,
        "https": proxy
    }
    payload = {
        'category': '',
        'news_offset': news_id
    }
    post_url = "https://inshorts.com/en/ajax/more_news"
    news = requests.post(post_url, payload, proxies=proxy_dict).json()
    return news


def content_sorter(html_data, news_id):
    html_data = html_data[html_data.find('<div class="news-card z-depth-1"') + 10:]

    while True:
        headline = html_data[html_data.find('itemprop="headline"') + len('itemprop="headline"') + 1:
                             html_data.find("</span>", html_data.find('itemprop="headline"') + len('itemprop="headline"'))]
        article_body = html_data[html_data.find('itemprop="articleBody">') + len('itemprop="articleBody">'):
                                 html_data.find('</div>', html_data.find('itemprop="articleBody">')
                                                + len('itemprop="articleBody">'))]
        date = html_data[html_data.find('<span class="date">') + len('<span class="date">'):
                         html_data.find('</span>', html_data.find('<span class="date">') + len('<span class="date">'))]
        source = html_data[html_data.find('href="', html_data.find('<div class="read-more">')) + len('href="'):
                           html_data.find('">', html_data.find('href="', html_data.find('<div class="read-more">'))
                                          + len('href="'))]
        data.append([news_id, date, headline, article_body, source])
        if html_data.find('<div class="news-card z-depth-1"') == -1:
            break
        html_data = html_data[html_data.find('<div class="news-card z-depth-1"') + 10:]


url = "https://inshorts.com/en/read"
session = requests.Session()
result = session.get(url)
html_code = result.text
min_news_id = html_code[html_code.find("min_news_id") + 15: html_code.find("\"", html_code.find("min_news_id") + 16)]

count = 0

while count < 1:
    json_news = load_news(min_news_id)
    html = json_news["html"]
    min_news_id = json_news["min_news_id"]
    content_sorter(html, min_news_id)
    time.sleep(5)
    count += 1

with open('news.csv', 'w+') as writefile:
    writer = csv.writer(writefile)
    writer.writerows(data)
