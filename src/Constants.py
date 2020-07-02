import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
DATABASE_URL = os.getenv('DATABASE_URL')
GUILD_ID = int(os.getenv("GUILD_ID"))
HACKERMAN_ID = int(os.getenv("HACKERMAN_ID"))
BOT_ID = int(os.getenv("BOT_ID"))
UKR_IDs = [int(os.getenv("UKR_1")), int(os.getenv("UKR_2"))]
ZAKHOZHKA_ID = int(os.getenv("ZAKHOZHKA_ID"))
GUILD = None
BOT = None
BARTENDER_ROLE = None
PEPEHACK_ROLE = None
FEMALE_ROLE = None
MAIN_CHANNEL = None
MUSIC_CHANNEL = None