import requests
import time
from datetime import datetime


API_URL= 'https://api.vk.com/method/'
ACCESS_TOKEN = '7e155b697a0c48aa1e6de8a212e9c2d0ed173354d5dbe0e9e79c68e758f1dea9aff25b1a0cac9364724c5'
V = '5.71'
METHODS = {'users.get':'users.get', 'screen.name':'utils.resolveScreenName', 'friends.get':'friends.get'}
DEFAULT_PARAMS = {'access_token':ACCESS_TOKEN, 'v':V}


def get_id(uid):
    r = requests.get(API_URL + METHODS['users.get'], params = {**DEFAULT_PARAMS, 'user_ids':uid})
    return r.json()['response'][0]['id']  # метод возвращающий id пользователя

def friends_get(uid):
    r = requests.get(API_URL + METHODS['friends.get'], params = {**DEFAULT_PARAMS, 'user_id':uid, 'fields':'bdate'})
    return r.json()['response']['items']


def bdate_get(uid):
    friendlist = friends_get(uid)
    friends_birthday_list = []
    for i in range(len(friendlist)):
        if 'bdate' in friendlist[i]:
            friends_birthday_list.append(friendlist[i]['bdate'])
    friends_birthday_list = list(filter(lambda s: len(s) > 5, friends_birthday_list))
    return friends_birthday_list  # метод возвращающий список дат рождения пользователей у которых указан год рождения

def calc_age(uid):
    id = get_id(uid)
    date_list = bdate_get(id)
    olds = []
    olds_freq = {}
    for i in range(len(date_list)):
        date_list[i] = date_list[i][len(date_list[i])-4:]
    current_year = datetime.utcnow().year
    for date in date_list:
        olds.append(current_year - int(date))
    for old in olds:
        if old not in olds_freq:
            k = 1
            olds_freq[old] = k
        else:
            olds_freq[old] += 1
    return sorted(olds_freq.items(), key=lambda x: (-x[1], x[0]))