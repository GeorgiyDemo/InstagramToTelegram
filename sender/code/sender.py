import json
import os
import re
import time

import redis
import requests
import telegram
from bs4 import BeautifulSoup


class Redis:
    """For Redis DB"""

    def __init__(self, r_passwd):
        self.r_table = redis.Redis(
            host="redis", port=6379, decode_responses=True, db=0, password=r_passwd
        )

    def get_data(self):
        """Getting list with media_ids from DB"""
        lst = []
        for key in self.r_table.keys():
            lst.append(key)
        return lst

    def set_data(self, key, value):
        """Writing new data to DB"""
        self.r_table.set(key, value)

    @property
    def data(self):
        """getter"""
        return self.get_data()

    @data.setter
    def data(self, ddict):
        """setter"""
        for sub in ddict.items():
            self.set_data(*sub)


class Instagram2Telegram:
    def __init__(self, token, tag, channel_name, r_passwd):

        # Redis connector
        self.r_obj = Redis(r_passwd)
        # Telegram bot
        self.bot = telegram.Bot(token)
        # User's URL
        self.username_url = "https://www.instagram.com/p/"
        # Main URL
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
        Main logic:
        1. Get saved media_ids form Redis
        2. Get new_media_id for the last Instagram post with tag 
        3. Compare that new_media_id is not in media_ids
        4. If step 3 was True, post media to Telegram channel & add new_media_id to Redis 
        """

        # Getting data from Redis
        media_ids = self.r_obj.data

        # Getting data from URL via self.getter
        result = self.getter(self.mainurl)
        tag_page = result["entry_data"]["TagPage"][0]["graphql"]["hashtag"][
            "edge_hashtag_to_media"
        ]["edges"][0]["node"]
        new_media_id = tag_page["id"]

        # If new_media_id is not in Redis --> this is a new photo/video that still not in Telegram
        if new_media_id not in media_ids:
            code = tag_page["shortcode"]
            username = self.getter(self.username_url + code)["entry_data"]["PostPage"][
                0
            ]["graphql"]["shortcode_media"]["owner"]["username"]

            # Add new_media_id to Redis
            self.r_obj.data = {new_media_id: username}

            # Post media to Telegram
            self.send_telegram(tag_page, username)

    def getter(self, url):
        """Page dumper with BeautifulSoup & lxml"""
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "lxml")
        script_tag = soup.find("script", text=re.compile("window\._sharedData"))
        shared_data = script_tag.string.partition("=")[-1].strip(" ;")
        result = json.loads(shared_data)
        return result

    def send_telegram(self, media_json, username):
        """Post media to Telegram"""

        media_text = media_json["edge_media_to_caption"]["edges"][0]["node"]["text"]
        media_url = media_json["display_url"]

        # Long text is not cool
        if len(media_text) > 201:
            media_text = ""

        # if video
        if media_json["is_video"]:
            caption = "By @" + username + "\n" + media_text

            buf_data = getter(self.username_url + media_json["shortcode"])
            media_url = buf_data["entry_data"]["PostPage"][0]["graphql"][
                "shortcode_media"
            ]["video_url"]

            self.bot.sendVideo(
                chat_id=self.channel_name, video=media_url, caption=caption
            )

        # if photo
        else:
            caption = "By @" + username + "\n" + media_text
            media_url = media_json["thumbnail_src"]
            self.bot.sendPhoto(
                chat_id=self.channel_name, photo=media_url, caption=caption
            )


def main():

    # Getting data from .env
    token = os.getenv("TELEGRAM_TOKEN", None)
    channel_name = os.getenv("TELEGRAM_CHANNELNAME", None)
    tag = os.getenv("INSTAGRAM_TAGNAME", None)
    r_passwd = os.getenv("REDIS_PASSWORD", None)

    Instagram2Telegram(token, tag, channel_name, r_passwd)


if __name__ == "__main__":
    main()
