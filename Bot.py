import csv
import datetime
import random
import traceback

import discord
import validators

import src.Constants as Constants
import src.Utility as Utility
from src.Alcoholic import Alcoholic
from src.Bartender import Bartender

client = discord.Client()

bartender = None
durka = dict()
heads = ['1Head', '2Head', '3Head', '4Head', '5Head', '6Head', 'fakeHead']

# Гачи функционал: список ссылок на ютуб видео, которые можно пополнять через дискорд и получать рандомную ссылку по запросу.
#TODO: На данный момент ссылки хранятся в .csv файле и подгружаются в сет gachi при запуске программы. Надо бы перенести их в базу данных 
gachi = []

# Добавляет ссылку в сет gachi и .csv файл. Возвращает True если ссылки не было до этого в листе, и была добавлена
def add_gachi(link):
    global gachi
    if link not in gachi:
        gachi.append(link)
        with open('Гачи.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([link,])
        return True
    else:
        return False

# Удаляет ссылку из сета gachi и .csv файла. Возвращает True если ссылка было до этого в листе, и была удалена
def remove_gachi(link):
    global gachi
    if link in gachi:
        gachi.remove(link)
        with open('Гачи.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            for row in gachi:
                writer.writerow([row,])
        return True
    else:
        return False

# Функция вызывается при запуске бота
@client.event
async def on_ready():
    random.seed()
    Constants.GUILD = discord.utils.get(client.guilds, id=Constants.GUILD_ID) 
    Constants.BOT = client.user
    Constants.BARTENDER_ROLE = discord.utils.get(Constants.GUILD.roles, name='Бармен')
    Constants.PEPEHACK_ROLE = discord.utils.get(Constants.GUILD.roles, name='Пепе-хацкер')
    Constants.FEMALE_ROLE = discord.utils.get(Constants.GUILD.roles, name='Шоу-GIRLS')
    Constants.MAIN_CHANNEL = discord.utils.get(Constants.GUILD.channels, name='флудилка')
    Constants.MUSIC_CHANNEL = discord.utils.get(Constants.GUILD.channels, name='музыкальный-автомат')

    global bartender
    bartender = Bartender()
    for member in Constants.GUILD.members:
        bartender.alcoholics[member.id] = Alcoholic()
    print(f'{client.user} is connected to {Constants.GUILD.name}')
    # Считывние ссылок из .csv файла в сет gachi при запуске
    global gachi
    with open('Гачи.csv', newline='') as gachi_file:
        gachi_reader = csv.reader(gachi_file)
        for row in gachi_reader:
            gachi.append(row[0])

# Реакция на присоединение юзера к серверу
@client.event
async def on_member_join(member):
    bartender.alcoholics[member.id] = Alcoholic()
    await Constants.MAIN_CHANNEL.send(f'Эй {member.mention}, присаживайся... или падай под барную стойку {Utility.emote("MHM")}')

# Реакция на ошибку в программе (необработанное исключение). Пишет в чат реакцию и скидывает в лс лог ошибки.
@client.event
async def on_error(event, *args, **kwargs):
    await Constants.MAIN_CHANNEL.send(f'Что-то пошло не так {Utility.emote("FeelsBanMan")}')
    for hackerman in Constants.PEPEHACK_ROLE.members:
        await client.get_user(hackerman.id).send(f'Ошибка в {event} \n{traceback.format_exc()}')  # Лог в лс
       
# Обработка команд при помощи чтения и сравнивания кождого сообщения с командой
#TODO: Возможно стоит перейти на фреймворк дискорда bot.command: больше возможностей, легче писать и поддержвать код, прямая поддержка дополнительных аргументов
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if ('бармен' in message.content.lower() or client.user.mention in message.content) and any(thanks in message.content.lower() for thanks in ['спасибо', 'благодарю', 'спс', 'благодарен']):
        if Utility.in_durka(message.author, durka):
            await message.channel.send(f'{message.author.mention}, Вы с кем разговариваете? {Utility.emote("durka")}')
        else:
            await bartender.reply_thanks(message.author, message.channel)

    elif message.content == '!БАРМЕН' or message.content.startswith('БАРМЕН'):
        await message.channel.send(f'{message.author.mention}, зачем Вы кричите на меня? {Utility.emote("pepeHands")}')

    elif message.content.lower() == '!бармен' or message.content.lower() == 'бармен?' or message.content.lower() == 'бармен!':
        if Utility.in_durka(message.author, durka):
            await message.channel.send(f'{message.author.mention}, Вы с кем разговариваете? {Utility.emote("durka")}')
        elif message.author.id == Constants.HACKERMAN_ID and message.content == 'бармен!':  # админская команда на активацию всякой всячины
            bartender.special = not bartender.special
            await message.channel.send(f'{message.author.mention}, я за барной стойкой! {Utility.emote("pepeClown")}')
        else:
            await message.channel.send(f'{message.author.mention}, я за барной стойкой! {Utility.emote("pepeOK")}')

    # !алко - проверяет степень опьянённости юзера
    if message.content == '!алко':
        if Utility.in_durka(message.author, durka):
            await message.channel.send(f'{message.author.mention}, опять за своё? {Utility.emote("durka")}')
        else:
            await bartender.check_alco(message.author, message.channel)

    # !алко [new_alco [@юзер]] - меняет степень опьянения юзера на new_aclo
    # если юзер не указан, действует на автора сообщения
    if message.content.startswith('!алко') and len(message.content.split()) > 1:
        if Utility.in_durka(message.author, durka):
            await message.channel.send(f'{message.author.mention}, опять за своё? {Utility.emote("durka")}')
            return

        user = message.author if (len(message.content.split()) == 2) else Utility.get_user_from_mention(message.content.split()[2])
        try:
            new_alco_percent = Utility.clip(int(message.content.split()[1]), 0, 100)
        except ValueError:
            new_alco_percent = None
            
        if new_alco_percent is not None and user:
            # шанс успеха команды зависит от разницы нового и старого значений
            # чем меньше разница, тем больше шанс на успех
            alco_diff = new_alco_percent - bartender.alcoholics[user.id].alco_test()
            success = random.randrange(101) >= abs(alco_diff)
            if message.content.split()[0] == '!алко_' and Utility.has_permissions(message.author):  # админская команда для 100% шанса на успех
                success = True
            elif bartender.alcoholics[user.id].timeout_mins_left() > 0:  # у полностью пьяного юзера нельзя менять степень опьянения
                success = False
        else:
            alco_diff = 0
            success = False
        if success and alco_diff != 0:
            bartender.alcoholics[user.id].remove_timeout()
            bartender.alcoholics[user.id].set_alco(new_alco_percent)
        await message.channel.send(choose_set_alco_phrase(message.author, user, alco_diff, success))

    # !выпить [напиток] - наливает автору напиток
    # если напиток не указан, наливает рандомный напиток
    if message.content.startswith('!выпить'):
        if Utility.in_durka(message.author, durka):
            await message.channel.send(f'Пожалуйста, {message.author.mention}, Ваше успокоительное {Utility.emote("durka")}')
        elif len(message.content.split()) > 1:
            drink = ' '.join(message.content.split()[1:])
            await bartender.give_drink(message.author, message.channel, drink)
        else:
            await bartender.give_drink(message.author, message.channel)


    if message.content == '!угостить барную стойку':
        if Utility.in_durka(message.author, durka):
            await message.channel.send(f'Пациент начинает буянить! {Utility.emote("durka")}')
            return
        voice_channel = discord.utils.get(Constants.GUILD.voice_channels, name='Ещё на барных стульях')
        for user in [u for u in voice_channel.members if u is not message.author]:
            if user.id in durka.keys() and durka[user.id].timeout_mins_left() > 0:
                await message.channel.send(f'{user.mention}, Вам {Utility.gender(message.author, "передал", "передала")} успокоительное ' +\
                    f'{Utility.gender(message.author, "Ваш вымышленный друг", "Ваша вымышленная подруга")} {message.author.mention} {Utility.emote("durka")}')
            else:
                await bartender.give_drink(user, message.channel, gift_giver=message.author)

    # !угостить (@юзер [напиток]) - наливает юзеру напиток
    # если напиток не указан, наливает рандомный напиток
    elif message.content.startswith('!угостить'):            
        if len(message.content.split()) <= 1:
            await message.channel.send(f'{message.author.mention}, кого угощать собрались? {Utility.emote("CoolStoryBob")}')
            return
        users = []
        drink = ' '.join(message.content.split()[2:]) if len(message.content.split()) > 2 else None
        if message.content.split()[1] == '@here' or message.content.split()[1] == '@everyone':
            if Utility.has_permissions(message.author):
                users = Utility.get_available_users(Constants.GUILD.members, [message.author, Constants.BOT])
            else:
                await message.channel.send(f'Сразу так много клиентов не смогу обслужить, простите {Utility.emote("FeelsBanMan")}')
                return
        else:
            voice_channel = discord.utils.get(Constants.GUILD.voice_channels, name=' '.join(message.content.split()[1:]))
            if voice_channel:
                for user in [u for u in voice_channel.members if u is not message.author]:
                    if user.id in durka.keys() and durka[user.id].timeout_mins_left() > 0:
                        await message.channel.send(f'{user.mention}, Вам {Utility.gender(message.author, "передал", "передала")} успокоительное ' +
                            f'{Utility.gender(message.author, "Ваш вымышленный друг", "Ваша вымышленная подруга")} {message.author.mention} {Utility.emote("durka")}')
                    else:
                        await bartender.give_drink(user, message.channel, gift_giver=message.author)
                return
            else:
                role = Utility.get_role_from_mention(message.content.split()[1])
                if role:
                    users = Utility.get_available_users(role.members, [message.author, Constants.BOT])
                    if not users and len(role.members) == 1 and message.author in role.members and not Utility.in_durka(message.author, durka):
                        await gift_drink_to_user(message.author, message.author, message.channel, drink, None)
                        return
                else:
                    user = Utility.get_user_from_mention(message.content.split()[1])
                    if user:
                        await gift_drink_to_user(message.author, user, message.channel, drink, None)
                    elif message.content.split()[1] == Utility.emote('YROD'):
                        user = discord.utils.get(Constants.GUILD.members, id=Constants.HACKERMAN_ID)
                        await gift_drink_to_user(message.author, user, message.channel, drink, False)
                        await message.channel.send(f'{user.mention}, ебать ты урод! {Utility.emote("YROD")}')
                    return
            if users:
                if Utility.in_durka(message.author, durka): # автор в дурке
                    await message.channel.send(f'{message.author.mention}, я так посмотрю у Вас слишком много друзей {Utility.emote("durka")}')
                else:
                    await gift_drink_to_multiple_users(message.author, users, message.channel, drink)
                return
            elif Utility.in_durka(message.author, durka):
                await message.channel.send(f'Таких пациентов пока не видел! {Utility.emote("durka")}')
            else:
                await message.channel.send(f'Извините, таких посетителей не видел')

    # !протрезветь [@юзер] - админская команда, снимающая эффект полного опьянения у юзера
    # если юзер не указан, действует на автора сообщения
    if message.content.startswith('!протрезветь'):
        user = message.author if len(message.content.split()) == 1 else Utility.get_user_from_mention(message.content.split()[1])
        if not user:
            await message.channel.send(f'{message.author.mention}, тебе бы самому протрезветь {Utility.emote("CoolStoryBob")}')
            return

        if Utility.in_durka(user, durka):
            await message.channel.send(f'{user.mention}, меньше пить надо было! {Utility.emote("durka")}')
            return

        if bartender.alcoholics[user.id].timeout_mins_left() > 0 or bartender.alcoholics[user.id].alco_test() != 0:
            # юзер пьян, проверяем на наличие админских прав
            if Utility.has_permissions(message.author): # админские права есть, снимаем опьянение и таймаут
                bartender.alcoholics[user.id].reset()
                bartender.alcoholics[user.id].hangover = False
                bartender.alcoholics[user.id].remove_timeout()
                if user is message.author:
                    await message.channel.send(f'{user.mention} принял анальгина и протрезвел {Utility.emote("pill")}')
                else:
                    await message.channel.send(f'{message.author.mention} дал {user.mention} анальгина, и {Utility.gender(user, "тот протрезвел.", "та протрезвела.")}')
            else:  # админских прав нет
                minutes_left = bartender.alcoholics[message.author.id].timeout_mins_left()
                if minutes_left > 0:
                    if user is message.author:
                        await message.channel.send(f'{user.mention}, тебе поможет только сон. {Utility.emote("Bored")} Приходи через {minutes_left} {Utility.minutes(minutes_left)}.')
                    else:
                        await message.channel.send(f'{message.author.mention} ' + Utility.gender(message.author, 'хотел', 'хотела') + \
                            f' позаботиться о {user.mention}, но {Utility.gender(user, "ему", "ей")} поможет только сон. {Utility.emote("Bored")}')
                elif user is message.author:
                    await message.channel.send(f'{user.mention}, а чё, слабо ещё выпить? {Utility.emote("3Head")}')
                else:
                    await message.channel.send(f'{message.author.mention} ' + Utility.gender(message.author, 'хотел', 'хотела') +\
                        f' позаботиться о {user.mention}, но {Utility.gender(user, "тот", "та")} и не думает прекращать веселье {Utility.emote("pepehype")}')
        elif user is message.author:  # юзер не пьян, ничего делать не надо
            await message.channel.send(f'{user.mention}, ты не выглядишь {Utility.gender(user, "пьяным", "пьяной")} {Utility.emote("pepeOK")}') 
        else:
            await message.channel.send(f'{message.author.mention}, зря беспокоишься, {user.mention} и так в порядке {Utility.emote("pepeOK")}') 

    ## Функционал гачи
    # !список_гачи - выдаёт полный список ссылок в канал дискорда
    if message.content == '!список_гачи':
        if message.channel.name != 'гачи':
            await message.channel.send(f'Hey {message.author.mention}, I think you got the wrong door. The leather-club is two blocks down.')
        else:
            gachi_list = ""
            MAX_STR_LEN = 2000
            async with message.channel.typing():
                for gach in gachi:
                    # Аккумулирует ссылки блоками до 2000 символов, выдаёт в несколько блоков весь список 
                    if len(gachi_list) + len(gach) >= MAX_STR_LEN:
                        await message.channel.send(gachi_list) 
                        gachi_list = ""
                    gachi_list += f'<{gach}> \n'
                await message.channel.send(gachi_list)   

    # !гачи - выдаёт рандомную ссылку из списка
    if message.content == '!гачи':
        if message.channel.name != 'гачи':
            await message.channel.send(f'Hey {message.author.mention}, I think you got the wrong door. The leather-club is two blocks down.')
        elif gachi:
            await message.channel.send(f'{str(random.choice(gachi))} \n{message.author.mention}, do you like what you see?')
        else:
            await message.channel.send('Oh shit, I\'m sorry')

    # !добавить_гачи (link) - добавляет ссылку в список гачи, если её ещё нет в списке
    if message.content.startswith('!добавить_гачи'):
        if message.channel.name != 'гачи':
            await message.channel.send(f'Hey {message.author.mention}, I think you got the wrong door. The leather-club is two blocks down.')
            return
        if len(message.content.split()) < 2:
            await message.channel.send(f'Fucking slave {message.author.mention}, укажи ссылку на трек! {Utility.emote("whip")}')
            return
        if message.content.split()[1][0] == '<':  # Скрытая ссылка формата <link>
            link = str(message.content.split()[1][1:-1])
        else:
            link = message.content.split()[1]
        if validators.url(link):  # Проверка ссылки на подходящий формат. Не проверяет на действительность.
            if add_gachi(link):
                await message.channel.send(random.choice(\
                    [f'I\'d be right happy to {Utility.emote("gachiS")}', \
                    f'Ass we can {Utility.emote("gachiS")}', \
                    f'Without further interruption let\'s celebrate and suck some dick {Utility.emote("gachiS")}']))
            else:
                await message.channel.send(f'Трек уже есть в гачи-автомате {Utility.emote("gachiS")}')
        else:
            await message.channel.send(f'{message.author.mention}, таких треков Dungeon Master не знает') 

    # !удалить_гачи (link) - удаляет ссылку из списка гачи, если она есть в списке
    if message.content.startswith('!удалить_гачи'):
        if message.channel.name != 'гачи':
            await message.channel.send(f'Hey {message.author.mention}, I think you got the wrong door. The leather-club is two blocks down.')
            return
        if len(message.content.split()) < 2:
            await message.channel.send(f'Fucking slave {message.author.mention}, укажи ссылку на трек! {Utility.emote("whip")}')
            return
        if message.content.split()[1][0] == '<':  # Скрытая ссылка формата <link>
            link = str(message.content.split()[1][1:-1])
        else:
            link = message.content.split()[1]
        if validators.url(link):  # Проверка ссылки на подходящий формат. Не проверяет на действительность.
            if remove_gachi(link):
                await message.channel.send(random.choice(\
                    [f'I\'d be right happy to {Utility.emote("gachiS")}', \
                    f'Ass we can {Utility.emote("gachiS")}', \
                    f'Without further interruption let\'s celebrate and suck some dick {Utility.emote("gachiS")}']))
            else:
                await message.channel.send(f'Трек не был найден в гачи-автомате {Utility.emote("gachiS")}')
        else:
            await message.channel.send(f'{message.author.mention}, таких треков Dungeon Master не знает')  

    ## Функционал дурки
    # !дурка [@юзер] - сажает юзера в дурку (изменение/запрет всех команд на x минут)
    # юзера может указать только человек с админскими правами
    # если юзер не указан, сажает в дурку автора сообщения
    if message.content.startswith('!дурка'):
        if len(message.content.split()) == 1:
            user = message.author
        elif Utility.has_permissions(message.author):
            user = Utility.get_user_from_mention(message.content.split()[1])
            if not user:  # был указан неверный юзер
                if Utility.in_durka(message.author, durka):
                    await message.channel.send(f'{message.author.mention}, Вы о ком говорите? {Utility.emote("durka")}')
                else:
                    await message.channel.send(f'{message.author.mention}, а может мы лучше Вас заберём? {Utility.emote("durka")}')
                return

        elif Utility.in_durka(message.author, durka):  # нет админских прав и был указан юзер
            # Автор сам находится в дурке
            await message.channel.send(f'{message.author.mention}, дружков своих подставить {Utility.gender(message.author, "решил?", "решила?")} {Utility.emote("durka")}')
            return
        else:
            await message.channel.send(f'{message.author.mention}, а может мы лучше Вас заберём? {Utility.emote("durka")}')
            return

        if user.id not in durka.keys():  # юзера нет в списке дурки, добавляем
            durka[user.id] = Alcoholic()
        if Utility.in_durka(user, durka):  # юзер уже в дурке
            minutes_left = durka[user.id].timeout_mins_left()
            if user is message.author:
                await message.channel.send(f'{message.author.mention}, куда {Utility.gender(message.author, "собрался?", "собралась?")}' +\
                    f' {Utility.emote("durka")} \nТебе сидеть в дурке ещё {minutes_left} {Utility.minutes(minutes_left)}!')
            else:
                await message.channel.send(f'{message.author.mention}, приказ уже выполнен! \n{user.mention} будет сидеть в дурке ещё {minutes_left} {Utility.minutes(minutes_left)}! \n')
        else:
            # Дурка реализована как статус опьянения (hangover). 
            # Так как все команды в дурке изменены это ничего не ломает и об этом невозможно узнать
            min_timeout = random.randrange(30, 40)
            durka[user.id].last_drink_time = datetime.datetime.now()
            durka[user.id].set_hangover(min_timeout)
            if user is message.author:
                await message.channel.send(f'{Utility.emote("durka")} увозим {message.author.mention} на {min_timeout} {Utility.minutes(min_timeout)}!\n' +\
                    f'{Utility.gender(message.author, "Молодой человек", "Девушка")}, пройдёмте... {Utility.emote("durka")}')
            else:    
                await message.channel.send(f'{user.mention}, на Вас поступила жалоба! {Utility.emote("durka")}\n' +\
                    f'За странное поведение увозим Вас на {min_timeout} {Utility.minutes(min_timeout)}!')

    # !выпустить [@юзер] - админская команда, выпускает юзера из дурки
    # если юзер не указан, выпускает автора сообщения
    if message.content.startswith('!выпустить'):
        user = message.author if len(message.content.split()) == 1 else Utility.get_user_from_mention(message.content.split()[1])

        if not user or user.id not in durka.keys():
            await message.channel.send(f'Таких пациентов не поступало... пока что {Utility.emote("durka")}')
        elif durka[user.id].timeout_mins_left() > 0:
            if Utility.has_permissions(message.author):
                durka[user.id].remove_timeout()
                await message.channel.send(f'Поступил приказ, выпускаем {user.mention} {Utility.emote("durka")}')
            elif user is not message.author:
                if not Utility.in_durka(message.author.id, durka): 
                    await message.channel.send(f'{message.author.mention}, а может мы лучше Вас заберём? {Utility.emote("durka")}')
                else:
                    await message.channel.send(f'Кажется, пациенты {message.author.mention} и {user.mention} планируют побег! {Utility.emote("monkaSpolice")}')
            else:
                minutes_left = durka[message.author.id].timeout_mins_left()
                await message.channel.send(f'{message.author.mention}, куда ' + Utility.gender(message.author, 'собрался?', 'собралась?') + \
                    f' {Utility.emote("durka")} \nТебе сидеть в дурке ещё {minutes_left} {Utility.minutes(minutes_left)}! \n')
        else: # юзера нет в дурке
            await message.channel.send(f'{Utility.gender(user, "Пациента", "Пациентку")} {user.mention} уже выпустили {Utility.emote("durka")}')

    # !буянить - юзер начинает буянить
    # Бот в зависимости от ситуации действует
    if message.content.startswith('!буянить'):
        if Utility.in_durka(message.author, durka):
            await message.channel.send(f'На вас надета смирительная рубашка, вы не сможете навредить {Utility.emote("durka")}')
        elif len(message.content.split()) > 1:
            user = Utility.get_user_from_mention(message.content.split()[1])
            if not user:
                role = Utility.get_role_from_mention(message.content.split()[1])
                if not role:
                    await message.channel.send(
                        f'Вы не находите {message.content.split()[1]} и бьете руками воздух!')
                else:
                    await message.channel.send(
                        f'Вы решили вызвать целый клан на бой, но все из клана "{role.mention}" смеются вам в лицо')
            else:
                await bartender.rage(message.author, message.channel, user)
        else:
            members = Utility.get_available_users(message.guild.members, [message.author, Constants.BOT], durka)
            await bartender.rage(message.author, message.channel, random.choice(members))

    if message.content == '!head':
        await message.channel.send(f'{message.author.mention}, сегодня ты')
        await message.channel.send(Utility.emote(random.choice(heads)))


    if message.content == '!альпака':
        if Utility.in_durka(message.author, durka):
            await message.channel.send(f'альпакА {Utility.emote("durka")}')
        else:
            await message.channel.send(Utility.emote("alpaka"))
            await message.channel.send(f'{Utility.emote("Pepega")} 📣 альпакА')


    if message.content == '!слава':
        if Utility.in_durka(message.author, durka):
            await message.channel.send(f'Ты что, хочешь чтобы было как на Украине? {Utility.emote("durka")}')
        elif message.channel == Constants.MUSIC_CHANNEL:
            await message.channel.send('!play <https://youtu.be/NluJAtDP2Ow>')
        elif message.author.id in Constants.UKR_IDs:
            await message.channel.send(Utility.emote("3Head") + " " + Utility.emote("UKR"))
        else:
            await message.channel.send('Вийди отсюда, розбiйник! Плохо чуеш мене?')


def choose_set_alco_phrase(author, user, alco_diff, success):
    if success:
        if user is author:
            if alco_diff < 0:
                return f'{author.mention} {Utility.gender(author, "разбавил", "разбавила")} водой свой напиток,' +\
                    f' и теперь {Utility.gender(author, "пьян", "пьяна")} на {bartender.alcoholics[author.id].alco_test()}% {Utility.emote("MHM")}'
            elif alco_diff == 0:
                return f'{author.mention}, ты и так {Utility.gender(author, "пьян", "пьяна")} на {bartender.alcoholics[author.id].alco_test()}% {Utility.emote("MHM")}'
            else:
                return f'{author.mention} {Utility.gender(author, "подмешал", "подмешала")} что-то себе в напиток,' +\
                    f' и теперь {Utility.gender(author, "пьян", "пьяна")} на {bartender.alcoholics[author.id].alco_test()}% {Utility.emote("monkaS")}'
        else:
            if alco_diff < 0:
                return f'{author.mention} {Utility.gender(author, "разбавил", "разбавила")} водой напиток {user.mention} \n' +\
                    f'Теперь {Utility.gender(user, "он", "она")} {Utility.gender(user, "пьян", "пьяна")} на {bartender.alcoholics[user.id].alco_test()}% {Utility.emote("MHM")}'
            elif alco_diff == 0:
                return f'{author.mention} {Utility.gender(author, "подмешал", "подмешала")} что-то {user.mention} в напиток \n' +\
                f'Это ничего не изменило, и {user.mention} до сих пор {Utility.gender(user, "пьян", "пьяна")} на {bartender.alcoholics[user.id].alco_test()}% {Utility.emote("MHM")}'
            else:
                return f'{author.mention} {Utility.gender(author, "подмешал", "подмешала")} что-то {user.mention} в напиток \n' +\
                    f'{user.mention} теперь {Utility.gender(user, "пьян", "пьяна")} на {bartender.alcoholics[user.id].alco_test()}% {Utility.emote("monkaS")}'
    elif user is author or user is None:
        return f'У {Utility.gender(author, "юного клофелинщика", "юной клофелинщицы")} {author.mention} ничего не получилось, и ' +\
        f'{Utility.gender(author, "он", "она")} до сих пор {Utility.gender(author, "пьян", "пьяна")}' +\
            f' на {bartender.alcoholics[author.id].alco_test()}% {Utility.emote("LULW")}'
    else:
        return f'У {Utility.gender(author, "юного клофелинщика", "юной клофелинщицы")} {author.mention} ничего не получилось, и {user.mention} до сих пор '+\
            f'{Utility.gender(user, "пьян", "пьяна")} на {bartender.alcoholics[user.id].alco_test()}% {Utility.emote("LULW")}'


async def gift_drink_to_user(author, user, channel, drink_name, give_compliment):
    if user == author:
        await channel.send(f'{user.mention}, у Вас биполярочка? {Utility.emote("durka")}')
    elif Utility.in_durka(author, durka):
        if Utility.in_durka(user, durka):  # автор и юзер в дурке
            await channel.send(f'{user.mention}, Вас {Utility.gender(author, "угостил", "угостила")}' +
                f'{author.mention}! Держите, Ваши антидепрессанты {Utility.emote("pill")} {Utility.emote("durka")}')
        else:  # только автор в дурке
            await channel.send(f'{user.mention}, Вам передачка из дурки! {author.mention} {Utility.gender(author, "угостил", "угостила")}' +
                f' Вас непонятными таблетками {Utility.emote("pill")} {Utility.emote("durka")}')
    elif Utility.in_durka(user, durka):  # только юзер в дурке
        await channel.send(random.choice( \
            [f'{author.mention}, а может мы лучше Вас заберём? {Utility.emote("durka")}', \
            f'{author.mention}, никаких передачек в дурку! {Utility.emote("durka")}']))
    else:
        await bartender.give_drink(user, channel, drink_name=drink_name, gift_giver=author, give_compliment=give_compliment)


async def gift_drink_to_multiple_users(author, users, channel, drink_name):
    for user in users:
        if user.id in durka.keys() and durka[user.id].timeout_mins_left() > 0:
            await channel.send(f'{user.mention}, Вам {Utility.gender(author, "передал", "передала")} успокоительное ' +
                f'{Utility.gender(author, "Ваш вымышленный друг", "Ваша вымышленная подруга")} {author.mention} {Utility.emote("durka")}')
        else:
            await bartender.give_drink(user, channel, drink_name=drink_name, gift_giver=author, give_compliment=None)

client.run(Constants.TOKEN)
