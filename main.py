import requests
import json
from tqdm import tqdm
from datetime import datetime

class VKGetPhotos:

    base_url = 'https://api.vk.com/method'

    def __init__(self, vk_token, user_id, yandex_token, count_photo=5):
        self.token_vk = vk_token
        self.headers = {
            'Authorization': 'OAuth ' + yandex_token
        }
        self.id = user_id
        self.params = {'access_token' : self.token_vk, 'v' : '5.199'}
        self.count_photo = count_photo
        self.all_photos = 0

    @staticmethod
    def _create_url(method):
        return f'{VKGetPhotos.base_url}/{method}'

    def get_photos(self):
        self.params.update({'owner_id' : self.id, 'album_id' : 'profile', 'extended' : 1, 'rev' : 1, 'count' : self.count_photo})
        response = requests.get(self._create_url('photos.get'), params=self.params)
        self.all_photos = response.json().get('response', {}).get('count')
        return response.json().get('response', {}).get('items')

    def create_dir_yandex(self, name_dir):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {
            'path': name_dir
        }
        try:
            response = requests.put(url, params=params, headers=self.headers)
            response.raise_for_status()
        except:
            requests.delete(url, params=params, headers=self.headers)
            response = requests.put(url, params=params, headers=self.headers)
            response.raise_for_status()
        return name_dir

    def get_filenames_dict(self):
        filenames = {}
        for photo in self.get_photos():
            max_height = 0
            max_width = 0
            max_type = 'base'
            sizes = photo.get('sizes', {})
            for size in sizes:
                if size['height'] > max_height and size['width'] > max_width:
                    max_height = size['height']
                    max_width = size['width']
                    max_type = size['type']
                    file_url = size['url']
            filename = photo.get('likes', {}).get('count')
            datetime_load = datetime.fromtimestamp(photo.get('date')).strftime('%Y-%m-%d')
            if filenames.get(filename):
                filename = f'{filename} - {datetime_load}.jpg'
                filenames[filename] = {'content_url' : requests.get(file_url).content, 'size' : max_type}
            else:
                filename = f'{filename}.jpg'
                filenames[filename] = {'content_url' : requests.get(file_url).content, 'size' : max_type}
        return filenames

    @staticmethod
    def create_logfile(data):
        with open('vk_logfile', 'w') as f:
            json.dump(data, f)

    def load_photos (self, name_dir):
        data_log = []
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        self.create_dir_yandex(name_dir)
        files = self.get_filenames_dict()
        progress_list = tqdm(files.keys(), ncols=80, colour='green')
        for filename in progress_list:
            data_log.append({"file_name": filename, 'size': files[filename]['size']})
            params = {
                'path': f'{name_dir}/{filename}'
            }
            response = requests.get(url, params=params, headers=self.headers)
            requests.put(response.json().get('href'), files[filename]['content_url'])
            progress_list.set_description(f"Processing {filename}")
        if self.count_photo > self.all_photos:
            return f'Общее количество фотографий: {self.all_photos}'
        self.create_logfile(data_log)


if __name__ == '__main__':
    token_vk = 'Введите ваш access_token'
    user_id_vk = 'Введите ваш user_id ВК'
    token_yandex = 'Введите ваш яндекс токен для авторизации'
    vk = VKGetPhotos(token_vk, user_id_vk, token_yandex, 2)
    vk.load_photos('vk')