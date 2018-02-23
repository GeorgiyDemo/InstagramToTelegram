import sys, os, json, requests, re, wget, time, telegram
from bs4 import BeautifulSoup
from telegram.ext import Updater

bot = telegram.Bot('YOUR_TELEGRAM_TOKEN')
tag = "INSTAGRAM_TAG"
channel_name = "@TELEGRAM_CHANNEL_NAME"

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

def start(bot, media_json, username):

	media_text = media_json["edge_media_to_caption"]["edges"][0]["node"]["text"]
	media_url = media_json["display_url"]

	if (len(media_text)>201):
		media_text = ""

	if (media_json["is_video"]==False):
		bot.sendPhoto(chat_id=channel_name, photo=media_json["thumbnail_src"], caption="By @"+username+"\n"+media_text)
	
	if (media_json["is_video"]==True):
		bot.sendVideo(chat_id=channel_name, video=getter(username_url+media_json["shortcode"])["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["video_url"], caption="От @"+username+"\n"+media_text)

InputWork()

while True:

	result = getter(mainurl)
	tag_page = result["entry_data"]["TagPage"][0]["graphql"]["hashtag"]["edge_hashtag_to_media"]["edges"][0]["node"]
	media_id = tag_page["id"]

	if ((media_id!=global_id) and (media_id!=previous_global_id)):
		OutWork(media_id,'DATA')
		InputWork()
		code = tag_page["shortcode"]
		username = getter(username_url+code)["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["owner"]["username"]
		start(bot,tag_page,username)

	time.sleep(10)