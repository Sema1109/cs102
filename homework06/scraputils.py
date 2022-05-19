import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore


def extract_news(parser):
    """Extract news from a given web page"""
    body = parser.findAll("table")[2]
    titles = [title.text for title in body.findAll("a", {"class": "titlelink"})]
    authors = [user.text for user in body.findAll("a", {"class": "hnuser"})]
    urls = [link["href"] for link in body.findAll("a", {"class": "titlelink"})]
    urls = ["https://news.ycombinator.com/" + url if url[:4] == "item" else url for url in urls]
    points = [score.text.split()[0] for score in body.findAll("span", {"class": "score"})]
    ids = [post["id"] for post in body.findAll("tr", {"class": "athing"})]
    discussions = [
        body.findAll("span", {"id": f"unv_{id}"})[0].findNext("a", {"href": f"item?id={id}"}).text
        for id in ids
    ]
    comments = [0 if element.isalpha() else int(element.split()[0]) for element in discussions]
    news_list = []
    for i, _ in enumerate(titles):
        news_list.append(
            {
                "author": authors[i],
                "comments": comments[i],
                "points": points[i],
                "title": titles[i],
                "url": urls[i],
            }
        )
    return news_list


def extract_next_page(parser):
    """Extract next page URL"""
    return parser.findAll("table")[2].findAll("a", {"class": "morelink"})[0]["href"]


def get_news(url, n_pages=1):
    """Collect news from a given web page"""
    news = []
    while n_pages:
        print("Collecting data from page: {}".format(url))
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        news_list = extract_news(soup)
        next_page = extract_next_page(soup)
        url = "https://news.ycombinator.com/" + next_page
        news.extend(news_list)
        n_pages -= 1
    return news
