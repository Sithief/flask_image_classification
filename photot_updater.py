import requests
import time
import logging
import configparser
import os
import database


class VkApi:
    def __init__(self, access_token, version='5.120'):
        self.vk_url = "https://api.vk.com/method/"
        self.token = access_token
        self.version = version
        self.VK_API = requests.Session()
        self.last_requests = []

    def request_get(self, method, parameters=None):
        if not parameters:
            parameters = {'access_token': self.token, 'v': self.version}
        if 'access_token' not in parameters:
            parameters.update({'access_token': self.token})
        if 'v' not in parameters:
            parameters.update({'v': self.version})

        while len(self.last_requests) >= 3:
            sleep_time = min(self.last_requests) + 1 - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)
            actual_time = time.time() - 1
            self.last_requests = [i for i in self.last_requests if actual_time < i]

        try:
            request_start = time.time()
            request = self.VK_API.post(self.vk_url + method, parameters, timeout=20)
            self.last_requests.append((time.time() + request_start) / 2)
            if request.status_code == 200:
                request = request.json()
                if 'error' in request and request['error']['error_code'] == 6:
                    return self.request_get(method, parameters)
                return request
            else:
                logging.error('request.status_code = ' + str(request.status_code))
                return {}

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
            logging.error('connection problems: ' + str(e))
            time.sleep(5)
            self.VK_API = requests.Session()
            return self.request_get(method, parameters)

        except Exception as e:
            logging.error('request_get: ' + str(e))
            return {}

    def get_friends(self, user_id='', fields=''):
        friends = self.request_get('friends.get', {'user_id': user_id,
                                                     'count': 5000,
                                                     'fields': fields})
        if 'response' not in friends:
            return []
        if friends['response']['count'] > 5000:
            friends2 = self.request_get('friends.get', {'user_id': user_id,
                                                          'count': 5000,
                                                          'offset': 5000,
                                                          'fields': fields})
            if 'response' in friends2:
                friends['response']['items'] += friends2['response']['items']
        return friends['response']['items']

    def get_photos(self, user_id, album_id='profile', count=100):
        photos = self.request_get('photos.get', {'user_id': user_id,
                                                 'album_id': album_id,
                                                 'sizes': 1,
                                                 'count': min(1000, count)})
        if 'response' not in photos:
            return []
        elif count > 1000 and photos['response']['count'] > 1000:
            for offset in range(1000, min(count, photos['response']['count']), 1000):
                photos2 = self.request_get('photos.get', {'user_id': user_id,
                                                          'album_id': album_id,
                                                          'sizes': 1,
                                                          'count': 1000,
                                                          'offset': offset})
                if 'response' in photos:
                    photos['response']['items'] += photos2['response']['items']
        return photos['response']['items']


def get_photos_urls(photos):
    urls = list()
    size_types = {'y': 807, 'x': 604, 'm': 130}
    max_key = lambda x: size_types.get(x['type'], 0)
    for photo in photos:
        max_photo_size = max(photo['sizes'], key=max_key)
        urls.append(max_photo_size['url'])
    return urls


def use_config(path=None):
    if not path:
        current_path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(current_path, 'config.cfg')
    conf = configparser.ConfigParser()
    conf.read(path, encoding='utf-8')
    vk = VkApi(conf.get('VK', 'token', fallback='no confirm'))
    return vk


def update_users(users):
    new_users_count = 0
    for user_id in users:
        if database.Users.query.filter_by(id=user_id).first() is None:
            new_user = database.Users(id=user_id, update_time=0)
            database.db.session.add(new_user)
            new_users_count += 1
    if new_users_count:
        database.db.session.commit()
    return new_users_count


def update_photos(photos):
    new_photos_count = 0
    for photo_url in photos:
        if database.Photos.query.filter_by(url=photo_url).first() is None:
            new_photo = database.Photos(url=photo_url, update_time=0)
            database.db.session.add(new_photo)
            new_photos_count += 1
    if new_photos_count:
        database.db.session.commit()
    return new_photos_count


if __name__ == "__main__":
    vk_api = use_config()
    friends = vk_api.get_friends()
    # print(f'find {update_users(friends)} new users')
    user_to_update = database.Users.query.order_by(database.Users.update_time).first()
    user_photos = vk_api.get_photos(user_to_update.id)
    photos_urls = get_photos_urls(user_photos)
    user_to_update.update_time = int(time.time())
    database.db.session.commit()
    print(f'find {update_photos(photos_urls)} new photos')
    # for fr in friends:
    #     user_photos = vk_api.get_photos(fr)
    #     user_photos = get_photos_urls(user_photos)
    #     print(user_photos)
    # print(friends)
