import json
import os
import re
import time

import redis
import requests
import telegram
from bs4 import BeautifulSoup


class Redis:
    """
    Класс для удобной работы с Redis
    В Redis хранятся ассоциации: media_id -> ник пользователя
    """

    def __init__(self, r_host, r_passwd):
        self.r_table = redis.Redis(host=r_host, port=6379, decode_responses=True, db=0, password=r_passwd)

    def get_data(self):
        """Получаем данные с таблицы, отдаем в виде dict"""
        lst = []
        for key in self.r_table.keys():
            lst.append(key)
        return lst

    def set_data(self, key, value):
        """Записываем данные в таблицу"""
        self.r_table.set(key, value)

    @property
    def data(self):
        return self.get_data()

    @data.setter
    def data(self, ddict):
        for sub in ddict.items():
            self.set_data(*sub)


class Instagram2Telegram:
    """Класс для перекидывания постов по тегу """

    def __init__(self, token, tag, channel_name, r_host, r_passwd):

        # Соединение с redis
        self.r_obj = Redis(r_host, r_passwd)
        # Бот телеграма
        self.bot = telegram.Bot(token)
        # URL пользователя
        self.username_url = "https://www.instagram.com/p/"
        # URL общий
        self.mainurl = "https://instagram.com/explore/tags/" + tag
        self.channel_name = channel_name

        while True:
            try:
                self.processing()
            except KeyError as e:
                print("KeyError:", e, e.args)
                continue
            time.sleep(10)

    def processing(self):
        """
        Вылавливание постов с инсты
        """
        # Получаем данные с Redis
        media_ids = self.r_obj.data

        # Получаем данные с url
        result = self.getter(self.mainurl)
        tag_page = result["entry_data"]["TagPage"][0]["graphql"]["hashtag"]["edge_hashtag_to_media"]["edges"][0]["node"]
        media_id = tag_page["id"]

        # Если id файла нет в списке всех файлов, то значит это новый файл
        if media_id not in media_ids:
            code = tag_page["shortcode"]
            username = \
            self.getter(self.username_url + code)["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["owner"][
                "username"]

            # Добавляем в Redis
            self.r_obj.data = {media_id: username}

            # Кидаем пост в Telegram
            self.send_telegram(tag_page, username)

    def getter(self, url):
        """
        Парсинг страницы с вложением 
        """
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "lxml")
        script_tag = soup.find("script", text=re.compile("window\._sharedData"))
        shared_data = script_tag.string.partition("=")[-1].strip(" ;")
        result = json.loads(shared_data)
        return result

    def send_telegram(self, media_json, username):
        """
        Отправка вложения в Telegram
        """

        media_text = media_json["edge_media_to_caption"]["edges"][0]["node"]["text"]
        media_url = media_json["display_url"]

        if (len(media_text) > 201):
            media_text = ""

        if not media_json["is_video"]:
            caption = "By @" + username + "\n" + media_text
            media_url = media_json["thumbnail_src"]
            self.bot.sendPhoto(chat_id=self.channel_name, photo=media_url, caption=caption)

        if media_json["is_video"]:
            caption = "By @" + username + "\n" + media_text

            buf_data = getter(self.username_url + media_json["shortcode"])
            media_url = buf_data["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["video_url"]

            self.bot.sendVideo(chat_id=self.channel_name, video=media_url, caption=caption)


def main():
    token = os.getenv('TELEGRAM_TOKEN', None)
    channel_name = os.getenv('TELEGRAM_CHANNELNAME', None)
    tag = os.getenv('INSTAGRAM_TAGNAME', None)
    r_host = os.getenv('REDIS_HOST', None)
    r_passwd = os.getenv('REDIS_PASSWORD', None)
    Instagram2Telegram(token, tag, channel_name, r_host, r_passwd)


if __name__ == "__main__":
    main()
