from scraputils import get_news  # type: ignore
from sqlalchemy import Column, Integer, String, create_engine  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore

Base = declarative_base()
engine = create_engine("sqlite:///news.db")
session = sessionmaker(bind=engine)


class News(Base):  # type: ignore
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    url = Column(String)
    comments = Column(Integer)
    points = Column(Integer)
    label = Column(String)


Base.metadata.create_all(bind=engine)


def fill_db(n_pages=10):
    s = session()
    news_list = get_news("https://news.ycombinator.com/newest", n_pages)
    for n in news_list:
        news = News(
            title=n["title"],
            author=n["author"],
            url=n["url"],
            comments=n["comments"],
            points=n["points"],
        )
        s.add(news)
    s.commit()
