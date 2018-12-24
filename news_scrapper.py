import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}


def load_news(news_id):
    payload = {
        'category': '',
        'news_offset': news_id
    }
    post_url = "https://inshorts.com/en/ajax/more_news"
    news = requests.post(post_url, payload).json()
    return news


url = "https://inshorts.com/en/read"
session = requests.Session()
result = session.get(url)
html_code = result.text
min_news_id = html_code[html_code.find("min_news_id") + 15: html_code.find("\"", html_code.find("min_news_id") + 16)]

