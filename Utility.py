import Constants
import discord

#Проверяет юзера на наличие админских прав
def has_permissions(user):
    return any(role in user.roles for role in [Constants.PEPEHACK_ROLE, Constants.BARTENDER_ROLE])

#Выбирает из 2 вариантов male/female в зависимости от наличия соответственной роли в дискорде
def gender(user, male, female):
    return female if Constants.FEMALE_ROLE in user.roles else male

#Выдаёт форматированный смайл с названием emote_name в формате строки для сообщения в дискорде
#Если смайла с данным именем нет на сервере, возвращаяется пустая строка
def emote(emote_name : str):
    emote = discord.utils.get(Constants.GUILD.emojis, name=emote_name)
    if emote is not None:
        return str(emote)
    else:
        return ''

#Возвращает id юзера типа int при заданном пинге юзера (отметка через @)
#В случае ошибки поднимает исключение ValueError
def get_id(user_mention : str):
    user_mention = user_mention.replace("<","")
    user_mention = user_mention.replace(">","")
    user_mention = user_mention.replace("@","")
    user_mention = user_mention.replace("!","")
    return int(user_mention)

#Выбирает подходящее окончание для "минуты" в зависимости от заданного количества минут 
def minutes(mins : int):
    if mins % 10 in [0, 5, 6, 7, 8, 9]:
        return 'минут'
    if mins % 10 in [2, 3, 4]:     
        return 'минуты'
    if mins % 10 == 1:     
        return 'минуту'

#Ограничивает x в пределах x_min, x_max
def clip(x, x_min, x_max):
    return max(x_min, min(x, x_max))