import string

from bayes import NaiveBayesClassifier
from bottle import redirect, request, route, run, template  # type: ignore
from db import News, session
from scraputils import get_news


@route("/")
@route("/news")
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template("news_template", rows=rows)


@route("/add_label/")
def add_label():
    zapros = request.query.decode()
    id = int(zapros["id"])
    label = zapros["label"]
    s = session()
    s.query(News).filter(News.id == id).update({News.label: label})
    s.commit()
    redirect("/news")


@route("/update")
def update_news():
    news = get_news("https://news.ycombinator.com/newest", 3)
    s = session()
    for new in news:
        if (
            len(s.query(News.author).filter_by(author="author").all()) == 0
            or len(s.query(News.title).filter_by(title="title").all()) == 0
        ):
            s.add(
                News(
                    title=new["title"],
                    author=new["author"],
                    url=new["url"],
                    points=new["points"],
                    comments=new["comments"],
                )
            )
    s.commit()
    redirect("/news")


def clean(s: str) -> str:
    translator = str.maketrans("", "", string.punctuation)
    return s.translate(translator)


@route("/classify")
def classify_news():
    s = session()
    classifier = NaiveBayesClassifier()
    X_train = [r.title for r in s.query(News).filter(News.label != None).all()][0:300]
    y_train = [r.label for r in s.query(News).filter(News.label != None).all()][0:300]
    predict_db = s.query(News).filter(News.label == None).all()
    X_predict = [r.title for r in predict_db][0:100]
    classifier.fit(X_train, y_train)
    labels = classifier.predict(X_predict)
    for i in range(100):
        predict_db[i].label = labels[i]
    classified = [x for x in predict_db if x.label == "good"]
    classified.extend([x for x in predict_db if x.label == "maybe"])
    classified.extend([x for x in predict_db if x.label == "never"])
    return template("recs", rows=classified)


@route("/recommendations")
def recommendations():
    global classifier
    if classifier:
        news_list = get_news("https://news.ycombinator.com/newest", 1)
        titles = [n["title"] for n in news_list]
        normalized_titles = []
        for title in titles:
            normalized_titles.append((title))
        labels = classifier.predict(normalized_titles)
        for i in range(len(news_list)):
            news_list[i]["label"] = labels[i]
        return template("news_recommendations", rows=news_list)
    else:
        return redirect("/classify")


if __name__ == "__main__":
    run(host="localhost", port=8011)
