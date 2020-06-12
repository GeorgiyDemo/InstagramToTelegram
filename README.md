## Instagram tag -> Telegram channel grabber

### How to use

1. Clone this repo
    ```console
    git clone https://github.com/GeorgiyDemo/InstagramToTelegram
    ```
2. Replace the strings in .env_example
    ```
    TELEGRAM_TOKEN=000000000:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    TELEGRAM_CHANNELNAME=@tg_channel_name
    INSTAGRAM_TAGNAME=inst_tag_without_#
    REDIS_PASSWORD=string_passwd
    ```
3. Rename .env_example to .env
4. Run via docker-compose
    ```console
    docker-compose up -d 
    ```

### Requirements

* docker-compose
* docker