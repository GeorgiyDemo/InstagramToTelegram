import sys, os, json, requests, re, wget, time, telegram
from bs4 import BeautifulSoup
from telegram.ext import Updater

bot = telegram.Bot('368637401:AAF--D8PxjFv_EcxZSbVoxFYaE_MUA6U2Zo')
tag = "Фото_КИП"
channel_name = "@photo_KIP"

base_url = "https://instagram.com/explore/tags/"
username_url ="https://www.instagram.com/p/"
mainurl = str(base_url + tag)

def InputWork():
	global global_id
	global previous_global_id
	f = open('DATA')
	tex = f.read().split(";")
	global_id = tex[0]
	previous_global_id = tex[1]
	f.close()

def OutWork(result,files):
    f = open(files, 'w')
    f.write(result+";"+global_id)
    f.close()

def getter(url):
	res = requests.get(url)
	soup = BeautifulSoup(res.text, "lxml")
	script_tag = soup.find("script", text=re.compile("window\._sharedData"))
	shared_data = script_tag.string.partition("=")[-1].strip(" ;")
	result = json.loads(shared_data)
	return result

#Telegram 
def start(bot, photo_url, caption_url, username):
	bot.sendPhoto(chat_id=channel_name, photo=photo_url, caption="От @"+username+"\n"+caption_url)

InputWork()

while True:

	result = getter(mainurl)
	tag_page = result["entry_data"]["TagPage"][0]["tag"]
	media = tag_page["media"]["nodes"]
	checker = tag_page["media"]
	
	if ((media[0]["id"]!=global_id) and (media[0]["id"]!=previous_global_id)):
		OutWork(media[0]["id"],'DATA')
		InputWork()

		code = media[0]["code"]
		username = getter(username_url+code)["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["owner"]["username"]
		print("РАБОТА")
		start(bot,media[0]["thumbnail_src"],media[0]["caption"],username)

	time.sleep(10)