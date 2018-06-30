import os

class Config(object):
    # get a token from @BotFather
    TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
    # the domain of your web server
    EXAMPLE_WEB_DOMAIN = os.environ.get("EXAMPLE_WEB_DOMAIN", "https://example.com")
    # the download location, where the HTTP Server runs
    DOWNLOAD_LOCATION = os.environ.get("DOWNLOAD_LOCATION", "DOWNLOADS")
    # Telegram maximum file upload size
    MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", 500000000))
    # The Telegram API things
    APP_ID = int(os.environ.get("APP_ID", 12345))
    API_HASH = os.environ.get("API_HASH", "")
    # variable for storing authorzied users
    AUTHORIZED_USERS = set(int(x) for x in os.environ.get("AUTHORIZED_USERS", "comma,seperated,TG,IDs").split(","))
    # for storing the Telethon session
    TL_SESSION = "madeline.session"
    # Python3 ReQuests CHUNK SIZE
    CHUNK_SIZE = 128
    # localhost PLEASE DO NOT CHANGE THIS VALUE #ForTheGreaterGood
    EXAMPLE_WEB_HOST = "0.0.0.0"
    EXAMPLE_WEB_PORT = int(os.environ.get("EXAMPLE_WEB_PORT", 8443))
    # for heroku specific things
    WEBHOOK = os.environ.get("WEBHOOK", None)
