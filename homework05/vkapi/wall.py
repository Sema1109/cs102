import textwrap
import time
import typing as tp
from string import Template

import pandas as pd
from pandas import json_normalize
from vkapi import config
from vkapi.exceptions import APIError
from vkapi.session import Session


def get_posts_2500(
    owner_id: str = "",
    domain: str = "",
    offset: int = 0,
    count: int = 10,
    max_count: int = 2500,
    filter: str = "owner",
    extended: int = 0,
    fields: tp.Optional[tp.List[str]] = None,
) -> tp.Dict[str, tp.Any]:
    pass


def get_wall_execute(
    owner_id: str = "",
    domain: str = "",
    offset: int = 0,
    count: int = 10,
    max_count: int = 2500,
    filter: str = "owner",
    extended: int = 0,
    fields: tp.Optional[tp.List[str]] = None,
    progress=None,
) -> pd.DataFrame:
    """
    Возвращает список записей со стены пользователя или сообщества.
    @see: https://vk.com/dev/wall.get
    :param owner_id: Идентификатор пользователя или сообщества, со стены которого необходимо получить записи.
    :param domain: Короткий адрес пользователя или сообщества.
    :param offset: Смещение, необходимое для выборки определенного подмножества записей.
    :param count: Количество записей, которое необходимо получить (0 - все записи).
    :param max_count: Максимальное число записей, которое может быть получено за один запрос.
    :param filter: Определяет, какие типы записей на стене необходимо получить.
    :param extended: 1 — в ответе будут возвращены дополнительные поля profiles и groups, содержащие информацию о пользователях и сообществах.
    :param fields: Список дополнительных полей для профилей и сообществ, которые необходимо вернуть.
    :param progress: Callback для отображения прогресса.
    """
    start = Session(config.VK_CONFIG["domain"])
    all_wall_posts = []
    for k in range(((count - 1) // max_count) + 1):
        try:
            code = Template(
                """var posts = []; var i = 0; while (i < $trys) {posts = posts + API.wall.get({"owner_id":$owner_id,"domain":"$domain","offset":$offset + i*100,"count":"$count","filter":"$filter","extended":$extended,"fields":'$fields',"v":$version})['items']; i=i+1;} return {'count': posts.length, 'items': posts};"""
            ).substitute(
                owner_id=owner_id if owner_id else 0,
                domain=domain,
                offset=offset + max_count * k,
                count=count - max_count * k if count - max_count * k < 101 else 100,
                trys=(count - max_count * k - 1) // 100 + 1
                if count - max_count * k < max_count + 1
                else max_count // 100,
                filter=filter,
                extended=extended,
                fields=fields,
                version=str(config.VK_CONFIG["version"]),
            )
            print(code)
            wall_posts = start.post(
                "execute",
                data={
                    "code": code,
                    "access_token": config.VK_CONFIG["access_token"],
                    "v": config.VK_CONFIG["version"],
                },
            )
            print(wall_posts)
            time.sleep(2)

            for one_post in wall_posts.json()["response"]["items"]:
                all_wall_posts.append(one_post)
            print(len(all_wall_posts))
        except:
            pass
    # return all_wall_posts
    return json_normalize(all_wall_posts)
