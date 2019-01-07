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
proxy_flag = 0
proxy_dict = {
    "https": '',
    "http": ''
}


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
                proxy_list.append([ip, port, scrapper_count-1])
        except Exception:
            break


def choose_proxies():
    if len(proxy_list) == 0:
        load_proxies()
    proxy = random.choice(proxy_list)
    final_proxy = proxy[0] + ":" + proxy[1]
    print("Current proxy is {}".format(final_proxy))
    return final_proxy


def load_news(news_id):
    global proxy_flag, proxy_dict
    if proxy_flag == 0:
        proxy = choose_proxies()
        proxy_dict['https'] = proxy
        proxy_dict['http'] = proxy
        proxy_flag = 1
    payload = {
        'category': '',
        'news_offset': news_id
    }
    post_url = "https://inshorts.com/en/ajax/more_news"
    while True:
        try:
            news = requests.post(post_url, payload, proxies=proxy_dict).json()
            break
        except (urllib3.exceptions.MaxRetryError, ConnectionRefusedError, requests.exceptions.ProxyError,
                urllib3.exceptions.NewConnectionError, requests.exceptions.SSLError):
            print("Updating the proxy...")
            ip = str(proxy_dict['https']).split(':')[0]
            for i in range(len(proxy_list)):
                if proxy_list[i][0] == ip:
                    proxy_list.pop(i)
                    print("Proxy list updated...")
                    break
            proxy = choose_proxies()
            proxy_dict['https'] = proxy
            proxy_dict['http'] = proxy
    return news


def content_sorter(html_data, news_id, code, latest_heading=''):
    html_data = html_data[html_data.find('<div class="news-card z-depth-1"') + 10:]

    while True:
        headline = html.unescape(html_data[html_data.find('itemprop="headline"') + len('itemprop="headline"') + 1:
                             html_data.find("</span>",
                                            html_data.find('itemprop="headline"') + len('itemprop="headline"'))])
        article_body = html.unescape(html_data[html_data.find('itemprop="articleBody">') + len('itemprop="articleBody">'):
                                 html_data.find('</div>', html_data.find('itemprop="articleBody">')
                                                + len('itemprop="articleBody">'))])
        date = html.unescape(html_data[html_data.find('<span class="date">') + len('<span class="date">'):
                         html_data.find('</span>', html_data.find('<span class="date">') + len('<span class="date">'))])
        source = html.unescape(html_data[html_data.find('href="', html_data.find('<div class="read-more">')) + len('href="'):
                           html_data.find('">', html_data.find('href="', html_data.find('<div class="read-more">'))
                                          + len('href="'))])
        if code == 0:
            with open('news.csv', 'a+') as write_file:
                content_to_write = [[news_id, date, headline, article_body, source]]
                writer = csv.writer(write_file)
                writer.writerows(content_to_write)
            if html_data.find('<div class="news-card z-depth-1"') == -1:
                break
        elif code == 1:
            data.append([news_id, date, headline, article_body, source])
            with open('latest_news.csv', 'w+') as write_latest_file:
                writer = csv.writer(write_latest_file)
                writer.writerows([[news_id, date, headline, article_body, source]])
            if headline == latest_heading:
                with open('news.csv', 'w') as write_file:
                    writer = csv.writer(write_file)
                    writer.writerows(data)
                    write_file.write(existing_news_data)
                break
            if html_data.find('<div class="news-card z-depth-1"') == -1:
                with open('news.csv', 'w') as write_file:
                    writer = csv.writer(write_file)
                    writer.writerows(data)
                    write_file.write("\n".join(existing_news_data))
                break
        else:
            date = html.unescape(date)
            headline = html.unescape(headline)
            article_body = html.unescape(article_body)
            source = html.unescape(source)
            data.append([news_id, date, headline, article_body, source])
            if html_data.find('<div class="news-card z-depth-1"') == -1:
                break

        html_data = html_data[html_data.find('<div class="news-card z-depth-1"') + 10:]


def get_latest_news():
    latest_heading = existing_news_data[0].split(',')[2]
    url = "https://inshorts.com/en/read"
    session = requests.Session()
    result = session.get(url)
    html_code = result.text
    min_news_id = html_code[
                  html_code.find("min_news_id") + 15: html_code.find("\"", html_code.find("min_news_id") + 16)]
    if html_code.__contains__(latest_heading):
        content_sorter(html_code, min_news_id, 1, latest_heading)
    else:
        while True:
            time.sleep(5)
            more_news = load_news(min_news_id)
            min_news_id = more_news["min_news_id"]
            html_news = more_news["html"]
            if html_news.__contains__(latest_heading):
                print("Heading matched...")
                content_sorter(html_news, min_news_id, 1, latest_heading)
                break
            else:
                print("Heading did not matched...Fetching more news...")
                content_sorter(html_news, min_news_id, 2)


try:
    with open('news.csv', 'r') as file:
        existing_news_data = file.read()
        existing_news_data = existing_news_data.split('\n')
        min_news_id = existing_news_data[-2]
        min_news_id = min_news_id.split(',')[0]
    get_latest_news()

except FileNotFoundError:
    url = "https://inshorts.com/en/read"
    session = requests.Session()
    result = session.get(url)
    html_code = result.text
    min_news_id = html_code[
                  html_code.find("min_news_id") + 15: html_code.find("\"", html_code.find("min_news_id") + 16)]

count = 1
while count <= 10:
    print("Iteration number {}...".format(count))
    json_news = load_news(min_news_id)
    html_ = json_news["html"]
    min_news_id = json_news["min_news_id"]
    content_sorter(html_, min_news_id, 0)
    time.sleep(5)  # So that there are not too many consecutive request and the server does not crash! :)
    count += 1

# TODO: Modify the news.csv file as it fetches the data. Because the code is still not full proof and can not afford
#  to put such much traffic
# TODO: Do not change the proxy if it works
