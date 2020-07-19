import datetime

import discord
import emojis

import src.Constants as Constants
from src.Alcoholic import Alcoholic


# Проверяет юзера на наличие админских прав
def has_permissions(user: discord.Member) -> bool:
    return any(role in user.roles for role in [Constants.PEPEHACK_ROLE, Constants.BARTENDER_ROLE])

# Выбирает из 2 вариантов male/female в зависимости от наличия соответственной роли в дискорде
def gender(user, male, female):
    return female if Constants.FEMALE_ROLE in user.roles else male

# Выдаёт форматированный смайл с названием emote_name в формате строки для сообщения в дискорде
# Если смайла с данным именем нет на сервере, возвращаяется пустая строка
def emote(emote_name: str) -> str:
    if (emote := discord.utils.get(Constants.GUILD.emojis, name=emote_name)):
        return str(emote)
    elif emojis.count(emojis.encode(f':{emote_name}:')) > 0:
        return emojis.encode(f':{emote_name}:')
    else:
        return ''

# Возвращает id юзера типа int при заданном пинге юзера (отметка через @)
# В случае ошибки поднимает исключение ValueError
def get_id(user_mention: str) -> int:
    user_mention = user_mention.replace("<", "")
    user_mention = user_mention.replace(">", "")
    user_mention = user_mention.replace("@", "")
    user_mention = user_mention.replace("!", "")
    user_mention = user_mention.replace("&", "")
    return int(user_mention)

# Выбирает подходящее окончание для "минуты" в зависимости от заданного количества минут
def minutes(mins: int) -> str:
    if mins % 10 in [0, 5, 6, 7, 8, 9]:
        return 'минут'
    if mins % 10 in [2, 3, 4]:
        return 'минуты'
    if mins % 10 == 1:
        return 'минуту'

# Ограничивает x в пределах x_min, x_max
def clip(x, x_min, x_max):
    return max(x_min, min(x, x_max))


# Возвращает юзера указанного через @
# Если юзер не найден или указание было неверным, возвращает None
def get_user_from_mention(mention: str) -> discord.Member:
    try:
        return discord.utils.get(Constants.GUILD.members, id=get_id(mention))
    except ValueError:
        return None

# Возвращает роль указанную через @
# Если роль не найдена или указание было неверным, возвращает None
def get_role_from_mention(mention: str) -> discord.Role:
    try:
        return discord.utils.get(Constants.GUILD.roles, id=get_id(mention))
    except ValueError:
        return None


def get_voice_channel_from_message(message: str) -> discord.VoiceChannel:
    return next((channel for channel in Constants.GUILD.voice_channels if channel.name.lower() in message.lower()), None)

# Возвращает лист юзеров из user_list, которые удовлетворяют следующие условия:
# Юзер онлайн, не имеет таймаута в дурке, и не входит в список banned_users
def get_available_users(users_list: list, banned_users: list, check_durka: bool = False) -> list:
    if check_durka:
        def is_available(u: discord.Member):
            return u.status is not discord.Status.offline and u not in banned_users and not Alcoholic(u.id).in_durka()
    else:
        def is_available(u: discord.Member):
            return u.status is not discord.Status.offline and u not in banned_users
    return [u for u in users_list if is_available(u)]


def is_yt_url(url: str) -> bool:
    return 'https://www.youtube.com' in url or 'https://youtu.be/' in url


def yt_url_is_long(url: str) -> bool:
    return 'https://www.youtube.com' in url


def shorten_yt_url(long_url: str) -> str:
    watch_id = long_url.replace('https://www.youtube.com/watch?v=', '')[0:11]
    if watch_id == long_url[0:11]:
        raise Exception('Wrong URL Format')
    return f'https://youtu.be/{watch_id}'

