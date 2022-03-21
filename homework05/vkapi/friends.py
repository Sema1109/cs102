import dataclasses
import math
import time

importtyping as tp

from vkapi import config, exceptions, session  # type: ignore

QueryParams = tp.Optional[tp.Dict[str, tp.Union[str, int]]]


@dataclasses.dataclass(frozen=True)
class FriendsResponse:
    count: int
    items: tp.Union[tp.List[int], tp.List[tp.Dict[str, tp.Any]]]


def get_friends(
    user_id: int,
    count: int = 5000,
    offset: int = 0,
    fields: tp.Optional[tp.List[str]] = None,
) -> FriendsResponse:
    """
    Получить список идентификаторов друзей пользователя или расширенную информацию
    о друзьях пользователя (при использовании параметра fields).
    :param user_id: Идентификатор пользователя, список друзей для которого нужно получить.
    :param count: Количество друзей, которое нужно вернуть.
    :param offset: Смещение, необходимое для выборки определенного подмножества друзей.
    :param fields: Список полей, которые нужно получить для каждого пользователя.
    :return: Список идентификаторов друзей пользователя или список пользователей.
    """
    params = {
        "access_token": config.VK_CONFIG["access_token"],
        "v": config.VK_CONFIG["version"],
        "count": count,
        "user_id": user_id if user_id else "",
        "fields": ",".join(fields) if fields else "",
        "offset": offset,
    }
    response = session.get("friends.get", params=params)
    if "error" in response.json() or not response.ok:
        raise exceptions.APIError(response.json()["error"]["error_msg"])
    return FriendsResponse(**response.json()["response"])


class MutualFriends(tp.TypedDict):
    id: int
    common_friends: tp.List[int]
    common_count: int


def get_mutual(
    source_uid: tp.Optional[int] = None,
    target_uid: tp.Optional[int] = None,
    target_uids: tp.Optional[tp.List[int]] = None,
    order: str = "",
    count: tp.Optional[int] = None,
    offset: int = 0,
    progress=None,
) -> tp.Union[tp.List[int], tp.List[MutualFriends]]:
    """
    Получить список идентификаторов общих друзей между парой пользователей.
    :param source_uid: Идентификатор пользователя, чьи друзья пересекаются с друзьями пользователя с идентификатором target_uid.
    :param target_uid: Идентификатор пользователя, с которым необходимо искать общих друзей.
    :param target_uids: Cписок идентификаторов пользователей, с которыми необходимо искать общих друзей.
    :param order: Порядок, в котором нужно вернуть список общих друзей.
    :param count: Количество общих друзей, которое нужно вернуть.
    :param offset: Смещение, необходимое для выборки определенного подмножества общих друзей.
    :param progress: Callback для отображения прогресса.
    """
    if not target_uids:
        if not target_uid:
            raise Exception
        target_uids = [target_uid]
    responses = []
    if progress:
        row = progress(range(math.ceil(len(target_uids) / 100)))
    else:
        row = range(math.ceil(len(target_uids) / 100))
    for n in row:
        params = {
            "access_token": config.VK_CONFIG["access_token"],
            "v": config.VK_CONFIG["version"],
            "target_uid": target_uid,
            "source_uid": source_uid,
            "target_uids": ", ".join(map(str, target_uids)),
            "order": order,
            "count": count,
            "offset": offset,
        }
        response = session.get(f"friends.getMutual", params=params)
        if response.status_code != 200:
            raise exceptions.APIError
        offset += 100
        if not isinstance(response.json()["response"], list):
            response.append(  # type: ignore
                MutualFriends(
                    id=response["response"]["id"],  # type: ignore
                    common_friends=response["response"]["common_friends"],  # type: ignore
                    common_count=response["response"]["common_count"],  # type: ignore
                )
            )
        else:
            responses.extend(response.json()["response"])
        time.sleep(1)
    return responses


if __name__ == "__main__":
    friends = get_friends(user_id=466736313).items
    print(friends)
    print(len(friends))
    print(get_mutual(source_uid =466736313, target_uids=[338503155]))  
