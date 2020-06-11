import sys, os, json, requests, re, wget, time, telegram
from bs4 import BeautifulSoup
from telegram.ext import Updater

#Вместо этого зафигачиваем Redis
"""
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
"""

def getter(url):
	res = requests.get(url)
	soup = BeautifulSoup(res.text, "lxml")
	script_tag = soup.find("script", text=re.compile("window\._sharedData"))
	shared_data = script_tag.string.partition("=")[-1].strip(" ;")
	result = json.loads(shared_data)
	return result

#Telegram 




class Instagram2Telegram:
	"""Класс для перекидывания постов по тегу """
	def __init__(self, token, tag, channel_name):
		#Бот телеграма
		self.bot = telegram.Bot(token)
		#URL пользователя
		self.username_url ="https://www.instagram.com/p/"
		#URL общий
		self.mainurl = "https://instagram.com/explore/tags/" + tag
		self.channel_name = channel_name
		#Получаем данные с Redis
		InputWork()

		while True:
			processing()
			time.sleep(10)

	def processing(self):
		"""
		Вылавливание постов с инсты
		"""
		#Получаем данные с url
		result = getter(mainurl)
		tag_page = result["entry_data"]["TagPage"][0]["graphql"]["hashtag"]["edge_hashtag_to_media"]["edges"][0]["node"]
		media_id = tag_page["id"]

		if ((media_id!=global_id) and (media_id!=previous_global_id)):
			#Добавляем в Redis
			OutWork(media_id,'DATA')
			InputWork()
			code = tag_page["shortcode"]
			username = getter(username_url+code)["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["owner"]["username"]
			send_telegram(bot,tag_page,username)


	def send_telegram(bot, media_json, username):

		media_text = media_json["edge_media_to_caption"]["edges"][0]["node"]["text"]
		media_url = media_json["display_url"]

		if (len(media_text)>201):
			media_text = ""

		elif not media_json["is_video"]:
			bot.sendPhoto(chat_id=channel_name, photo=media_json["thumbnail_src"], caption="By @"+username+"\n"+media_text)
		
		elif media_json["is_video"]:
			bot.sendVideo(chat_id=channel_name, video=getter(username_url+media_json["shortcode"])["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["video_url"], caption="By @"+username+"\n"+media_text)


def main():
	token = os.getenv('TELEGRAM_TOKEN', None)
	channel_name = os.getenv('TELEGRAM_CHANNELNAME', None)
	tag = os.getenv('INSTAGRAM_TAGNAME', None)

	obj = Instagram2Telegram(token, tag, channel_name)
	

if __name__ == "__main__":
	main()