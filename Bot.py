import csv
import datetime
import random
import traceback
from math import ceil

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
    Constants.BARTENDER_ROLE = discord.utils.get(Constants.GUILD.roles, name='Бармен')
    Constants.PEPEHACK_ROLE = discord.utils.get(Constants.GUILD.roles, name='Пепе-хацкер')
    Constants.FEMALE_ROLE = discord.utils.get(Constants.GUILD.roles, name='Шоу-GIRLS')
    Constants.MAIN_CHANNEL = discord.utils.get(Constants.GUILD.channels, name='флудилка')
    Constants.MUSIC_CHANNEL = discord.utils.get(Constants.GUILD.channels, name='музыкальный-автомат')

    global bartender
    bartender = Bartender()
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
    await Constants.MAIN_CHANNEL.send('Эй ' + member.mention + f', присаживайся... или падай под барную стойку {Utility.emote("MHM")}')

# Реакция на ошибку в программе (необработанное исключение). Пишет в чат реакцию и скидывает в лс лог ошибки.
@client.event
async def on_error(event, *args, **kwargs):
    await Constants.MAIN_CHANNEL.send(f'Что-то пошло не так {Utility.emote("FeelsBanMan")}')
    hackermen = []
    for member in Constants.MAIN_CHANNEL.members:
        for role in member.roles:
            if role.name == "Пепе-хацкер":
                hackermen.append(member)
    print(hackermen)
    for hackerman in hackermen:
        await client.get_user(hackerman.id).send('Ошибка в ' + event + '\n' + traceback.format_exc())  # Лог в лс
       
# Обработка команд при помощи чтения и сравнивания кождого сообщения с командой
#TODO: Возможно стоит перейти на фреймворк дискорда bot.command: больше возможностей, легче писать и поддержвать код, прямая поддержка дополнительных аргументов
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    ''' Интерактив с барменом
    TODO: Можно добавить больше реакций на разные сообщения по типу приветствий, доброе утро/день/вечер/ночь и т.д.
          главное - чтоб не было слишком много лишних срабатываний и бот не реагировал на всё подряд
          при этом желательно сделать всё не в виде команд, а более похожим на диалог, 
          чтоб было максимально много интуитивных возможностей тригернуть реакцию, и не надо было вспоминать какая команда требуется для нужного ответа
          эти два условия довольно сложно совместить
    '''
    if ('бармен' in message.content.lower() or client.user.mention in message.content) and any(thanks in message.content.lower() for thanks in ['спасибо', 'благодарю', 'спс', 'благодарен']):
        if message.author.id in durka.keys() and durka[message.author.id].timeout_untill > datetime.datetime.now():
            await message.channel.send(f'{message.author.mention}, Вы с кем разговариваете? {Utility.emote("durka")}')
        else:
            await bartender.reply_thanks(message.author, message.channel)


    elif message.content == '!БАРМЕН' or message.content.startswith('БАРМЕН'):
        await message.channel.send(f'{message.author.mention}, зачем Вы кричите на меня? {Utility.emote("pepeHands")}')


    elif message.content.lower() == '!бармен' or message.content.lower() == 'бармен?' or message.content.lower() == 'бармен!':
        if message.author.id in durka.keys() and durka[message.author.id].timeout_untill > datetime.datetime.now():
            await message.channel.send(f'{message.author.mention}, Вы с кем разговариваете? {Utility.emote("durka")}')
        else:
            if message.author.id == Constants.HACKERMAN_ID and message.content == 'бармен!':  # админская команда на активацию всякой всячины
                bartender.special = not bartender.special
                await message.channel.send(f'{message.author.mention}, я за барной стойкой! {Utility.emote("pepeClown")}')
            else:
                await message.channel.send(f'{message.author.mention}, я за барной стойкой! {Utility.emote("pepeOK")}')

    ''' Основные команды бармена '''
    # !алко - проверяет степень опьянённости юзера
    if message.content == '!алко':
        if message.author.id in durka.keys() and durka[message.author.id].timeout_untill > datetime.datetime.now():
            await message.channel.send(f'{message.author.mention}, опять за своё? {Utility.emote("durka")}')
        else:
            if message.author.id not in bartender.alcoholics.keys():
                bartender.alcoholics[message.author.id] = Alcoholic()
            elif bartender.alcoholics[message.author.id].alco_test() == 0: 
                bartender.alcoholics[message.author.id].reset()
            elif not bartender.alcoholics[message.author.id].hangover: # обновляет значение восстановления, если юзер не полностью пьян
                bartender.alcoholics[message.author.id].recover()

            if bartender.alcoholics[message.author.id].timeout_untill < datetime.datetime.now() and bartender.alcoholics[message.author.id].hangover is True:  
                # тайамут из-за полного опьянения был, но прошёл. обнуляем значения, и поднимаем процент оставшегося опьянения до рандомного значения
                bartender.alcoholics[message.author.id].reset()
                bartender.alcoholics[message.author.id].alco_percent = random.randrange(30, 70)
            alco_test = bartender.alcoholics[message.author.id].alco_test()
            if alco_test == 100:
                await message.channel.send(random.choice(\
                    [f'{message.author.mention}, выглядишь на все :100: {Utility.emote("MonkaChrist")}', \
                    f'{message.author.mention}, ты {Utility.gender(message.author, "пьян", "пьяна")} на 100% {Utility.emote("Pepechill")} \nИди проспись! {Utility.emote("MHM")}']))
            else:
                await message.channel.send(f'{message.author.mention}, ты {Utility.gender(message.author, "пьян", "пьяна")} на {bartender.alcoholics[message.author.id].alco_test()}% {Utility.emote("Pepechill")}')

    # !алко [new_alco [@юзер]] - меняет степень опьянения юзера на new_aclo
    # если юзер не указан, действует на автора сообщения
    if message.content.startswith('!алко') and len(message.content.split()) > 1:
        if message.author.id in durka.keys() and durka[message.author.id].timeout_untill > datetime.datetime.now():
            # юзер в дурке
            await message.channel.send(f'{message.author.mention}, опять за своё? {Utility.emote("durka")}')
            return
        
        if len(message.content.split()) == 2:
            user = message.author
        else:
            try:
                user = discord.utils.get(message.guild.members, id=Utility.get_id(message.content.split()[2]))
            except ValueError:
                user = None
        try:
            new_alco_percent = Utility.clip(int(message.content.split()[1]), 0, 100)
        except ValueError:
            non_int = True
        else:
            non_int = False
            
        if user is not None and user.id not in bartender.alcoholics.keys():
            bartender.alcoholics[user.id] = Alcoholic()
        if not non_int and user is not None:
            # шанс успеха команды зависит от разницы нового и старого значений
            # чем меньше разница, тем больше шанс на успех
            alco_diff = new_alco_percent - bartender.alcoholics[user.id].alco_test()
            success = random.randrange(101) >= abs(alco_diff)
            if bartender.alcoholics[user.id].alco_test() == 100:  # у полностью пьяного юзера нельзя менять степень опьянения
                success = False
            if message.content.split()[0] == '!алко_' and Utility.has_permissions(message.author):  # админская команда для 100% шанса на успех
                success = True
        else:
            success = False
        if success:
            if alco_diff != 0:
                if bartender.alcoholics[message.author.id].timeout_untill > datetime.datetime.now() and new_alco_percent < 100:
                    bartender.alcoholics[message.author.id].timeout_untill = datetime.datetime.now() - datetime.timedelta(hours=1)
                    bartender.alcoholics[message.author.id].hangover = False
                bartender.alcoholics[user.id].reset()
                bartender.alcoholics[user.id].last_drink_time = datetime.datetime.now()  # изменение степени опьянения засчитывается как напиток
                bartender.alcoholics[user.id].alco_percent = new_alco_percent
                if bartender.alcoholics[user.id].alco_test() == 100:
                    bartender.alcoholics[user.id].set_hangover(random.randrange(20, 40))
                if user is message.author:
                    if alco_diff < 0:
                        await message.channel.send(f'{message.author.mention} {Utility.gender(message.author, "разбавил", "разбавила")} водой свой напиток, и теперь {Utility.gender(message.author, "пьян", "пьяна")} на {bartender.alcoholics[message.author.id].alco_test()}% {Utility.emote("MHM")}')
                    else:
                        await message.channel.send(f'{message.author.mention} {Utility.gender(message.author, "подмешал", "подмешала")} что-то себе в напиток, и теперь {Utility.gender(message.author, "пьян", "пьяна")} на {bartender.alcoholics[message.author.id].alco_test()}% {Utility.emote("monkaS")}')
                else:
                    if alco_diff < 0:
                        await message.channel.send(f'{message.author.mention} {Utility.gender(message.author, "разбавил", "разбавила")} водой напиток {user.mention} \nТеперь {Utility.gender(user, "он", "она")} {Utility.gender(user, "пьян", "пьяна")} на {bartender.alcoholics[user.id].alco_test()}% {Utility.emote("MHM")}')
                    else:
                        await message.channel.send(f'{message.author.mention} {Utility.gender(message.author, "подмешал", "подмешала")} что-то {user.mention} в напиток \n{user.mention} теперь {Utility.gender(user, "пьян", "пьяна")} на {bartender.alcoholics[user.id].alco_test()}% {Utility.emote("monkaS")}')
            else:
                if user is message.author:
                    await message.channel.send(f'{message.author.mention}, ты и так {Utility.gender(message.author, "пьян", "пьяна")} на {bartender.alcoholics[message.author.id].alco_test()}% {Utility.emote("MHM")}')
                else:
                    await message.channel.send(f'{message.author.mention} {Utility.gender(message.author, "подмешал", "подмешала")} что-то {user.mention} в напиток \nЭто ничего не изменило, и {user.mention} до сих пор {Utility.gender(user, "пьян", "пьяна")} на {bartender.alcoholics[user.id].alco_test()}% {Utility.emote("MHM")}')
        else:
            if user is message.author or user is None:
                await message.channel.send(f'У ' + Utility.gender(message.author, 'юного клофелинщика ', 'юной клофелинщицы ') + f'{message.author.mention} ничего не получилось, и ' + \
                Utility.gender(message.author, 'он', 'она') + ' до сих пор ' + Utility.gender(message.author, 'пьян', 'пьяна') + \
                    f' на {bartender.alcoholics[message.author.id].alco_test()}% {Utility.emote("LULW")}')
            else:
                await message.channel.send(f'У ' + Utility.gender(message.author, 'юного клофелинщика ', 'юной клофелинщицы ') + \
                    f'{message.author.mention} ничего не получилось, и {user.mention} до сих пор ' + Utility.gender(user, 'пьян', 'пьяна') + \
                    f' на {bartender.alcoholics[user.id].alco_test()}% {Utility.emote("LULW")}')

    # !выпить [напиток] - наливает автору напиток
    # если напиток не указан, наливает рандомный напиток
    if message.content.startswith('!выпить'):
        if message.author.id in durka.keys() and durka[message.author.id].timeout_untill > datetime.datetime.now():
            await message.channel.send(f'Пожалуйста, {message.author.mention}, Ваше успокоительное {Utility.emote("durka")}')
        else:
            if len(message.content.split()) > 1:
                drink = ' '.join(message.content.split()[1:])
                await bartender.give_drink(message.author, message.channel, drink)
            else:
                await bartender.give_drink(message.author, message.channel) 

    if message.content == '!угостить барную стойку':
        if message.author.id in durka.keys() and durka[message.author.id].timeout_untill > datetime.datetime.now():
            await message.channel.send(f'Пациент начинает буянить! {Utility.emote("durka")}')
            return
        voice_channel = discord.utils.get(Constants.GUILD.voice_channels, name='Ещё на барных стульях')
        for user in voice_channel.members:
            if user is not message.author:
                if user.id in durka.keys() and durka[user.id].timeout_untill > datetime.datetime.now():
                    await message.channel.send(f'{user.mention}, Вам {Utility.gender(message.author, "передал", "передала")} успокоительное ' +\
                        f'{Utility.gender(message.author, "Ваш вымышленный друг", "Ваша вымышленная подруга")} {message.author.mention} {Utility.emote("durka")}')
                else:
                    await bartender.give_drink(user, message.channel, gift_giver=message.author)

    # !угостить (@юзер [напиток]) - наливает юзеру напиток
    # если напиток не указан, наливает рандомный напиток
    elif message.content.startswith('!угостить'):
        if len(message.content.split()) > 1:
            try:
                user = discord.utils.get(message.guild.members, id=Utility.get_id(message.content.split()[1]))
            except ValueError:
                if message.content.split()[1] == Utility.emote('YROD'):
                    user = discord.utils.get(Constants.GUILD.members, id=Constants.HACKERMAN_ID)
                else:
                    user = None
            if user is None:
                if message.author.id in durka.keys() and durka[message.author.id].timeout_untill > datetime.datetime.now():
                    # автор в дурке и юзер не найден
                    await message.channel.send(f'Таких пациентов пока не видел! {Utility.emote("durka")}')
                    return
                else:
                    await message.channel.send(f'Извините, таких посетителей не видел')
                    return
            elif user is message.author:
                await message.channel.send(f'{message.author.mention}, у Вас биполярочка? {Utility.emote("durka")}')
                return
            if message.author.id in durka.keys() and durka[message.author.id].timeout_untill > datetime.datetime.now():
                if user.id in durka.keys():
                    # автор и юзер в дурке
                    await message.channel.send(f'{user.mention}, Вас {Utility.gender(message.author, "угостил", "угостила")} {message.author.mention}! Держите, Ваши антидепрессанты {Utility.emote("pill")} {Utility.emote("durka")}')
                    return
                else:
                    # только автор в дурке
                    await message.channel.send(f'{user.mention}, Вам передачка из дурки! {message.author.mention} {Utility.gender(message.author, "угостил", "угостила")} Вас непонятными таблетками {Utility.emote("pill")} {Utility.emote("durka")}')
                    return

            if user.id in durka.keys() and durka[user.id].timeout_untill > datetime.datetime.now():
                # только юзер в дурке
                await message.channel.send(random.choice( \
                    [f'{message.author.mention}, а может мы лучше Вас заберём? {Utility.emote("durka")}', \
                    f'{message.author.mention}, никаких передачек в дурку! {Utility.emote("durka")}']))
                return

            if len(message.content.split()) == 2: # рандомный напиток, не указан в сообщении
                if message.content.split()[1] == Utility.emote('YROD'):
                    await bartender.give_drink(user, message.channel, gift_giver=message.author, give_compliment=False)
                else:
                    await bartender.give_drink(user, message.channel, gift_giver=message.author) 
            else:  # напиток указан в сообщении
                drink = ' '.join(message.content.split()[2:])  # название напитка
                if message.content.split()[1] == Utility.emote('YROD'):
                    await bartender.give_drink(user, message.channel, gift_giver=message.author, give_compliment=False)
                else:
                    await bartender.give_drink(user, message.channel, drink, gift_giver=message.author)
            if message.content.split()[1] == Utility.emote('YROD'):
                await message.channel.send(f'{user.mention}, ебать ты урод! {Utility.emote("YROD")}')
        else:
            await message.channel.send(f'{message.author.mention}, кого угощать собрались? {Utility.emote("CoolStoryBob")}')

    # !протрезветь [@юзер] - админская команда, снимающая эффект полного опьянения у юзера
    # если юзер не указан, действует на автора сообщения
    if message.content.startswith('!протрезветь'):
        if len(message.content.split()) == 1:
            user = message.author
        else:
            try:
                user = discord.utils.get(message.guild.members, id=Utility.get_id(message.content.split()[1]))
            except ValueError:
                user = None
        if user.id not in bartender.alcoholics.keys():
            bartender.alcoholics[user.id] = Alcoholic()      
        if user.id in durka.keys() and durka[user.id].timeout_untill > datetime.datetime.now():
            await message.channel.send(f'{user.mention}, меньше пить надо было! {Utility.emote("durka")}')
            return

        if bartender.alcoholics[user.id].timeout_untill > datetime.datetime.now() or bartender.alcoholics[user.id].alco_test() == 100:
            # юзер пьян, проверяем на наличие админских прав
            if bartender.alcoholics[user.id].timeout_untill < datetime.datetime.now():
                # юзер полностью пьян, но таймаут ещё не был выдан (такого не должно быть)
                bartender.alcoholics[user.id].set_hangover(random.randrange(20, 40))
            if Utility.has_permissions(message.author): # админские права есть, снимаем опьянение и таймаут
                bartender.alcoholics[user.id].reset()
                bartender.alcoholics[user.id].hangover = False
                bartender.alcoholics[user.id].timeout_untill = datetime.datetime.now() - datetime.timedelta(hours=1)
                if user is message.author:
                    await message.channel.send(f'{user.mention} принял анальгина и протрезвел {Utility.emote("pill")}')
                else:
                    await message.channel.send(f'{message.author.mention} дал {user.mention} анальгина, и {Utility.gender(user, "тот протрезвел.", "та протрезвела.")}')
            else:  # админских прав нет
                minutes_left = ceil((bartender.alcoholics[user.id].timeout_untill - datetime.datetime.now()).total_seconds() / 60)
                if user is message.author:
                    await message.channel.send(f'{user.mention}, тебе поможет только сон. {Utility.emote("Bored")} Приходи через {minutes_left} {Utility.minutes(minutes_left)}.')
                else:
                    await message.channel.send(f'{message.author.mention} ' + Utility.gender(message.author, 'хотел', 'хотела') + \
                        f' позаботиться о {user.mention}, но {Utility.gender(user, "ему", "ей")} поможет только сон. {Utility.emote("Bored")}')
        else: # юзер не пьян, ничего делать не надо
            if user is message.author:
                await message.channel.send(f'{user.mention}, ты не выглядишь {Utility.gender(user, "пьяным", "пьяной")} {Utility.emote("pepeOK")}') 
            else:
                await message.channel.send(f'{message.author.mention}, зря беспокоишься, {user.mention} и так в порядке {Utility.emote("pepeOK")}') 

    '''Функционал гачи'''
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
        else:
            if len(gachi) > 0:
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
        #TODO: Можно добавить проверку на действительность ссылки.
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

    '''Функционал дурки'''
    # !дурка [@юзер] - сажает юзера в дурку (изменение/запрет всех команд на x минут)
    # юзера может указать только человек с админскими правами
    # если юзер не указан, сажает в дурку автора сообщения
    if message.content.startswith('!дурка'):
        if len(message.content.split()) == 1:
            user = message.author
        elif Utility.has_permissions(message.author):
            try:
                user = discord.utils.get(message.guild.members, id=Utility.get_id(message.content.split()[1]))
            except ValueError:
                user = None
        else:  # нет админских прав и был указан юзер
            if message.author.id in durka.keys() and durka[message.author.id].timeout_untill > datetime.datetime.now():  # Автор сам находится в дурке
                await message.channel.send(f'{message.author.mention}, дружков своих подставить {Utility.gender(message.author, "решил?", "решила?")} {Utility.emote("durka")}')
            else:
                await message.channel.send(f'{message.author.mention}, а может мы лучше Вас заберём? {Utility.emote("durka")}')
            return

        if user is None:  # был указан неверный юзер
            if message.author.id in durka.keys() and durka[message.author.id].timeout_untill > datetime.datetime.now():
                await message.channel.send(f'{message.author.mention}, Вы о ком говорите? {Utility.emote("durka")}')
            else:
                await message.channel.send(f'{message.author.mention}, а может мы лучше Вас заберём? {Utility.emote("durka")}')
            return

        if user.id not in durka.keys():  # юзера нет в списке дурки, добавляем
            durka[user.id] = Alcoholic()
        if durka[user.id].timeout_untill > datetime.datetime.now():  # юзер уже в дурке
            minutes_left = ceil((durka[user.id].timeout_untill - datetime.datetime.now()).total_seconds() / 60)
            if user is message.author:
                await message.channel.send(f'{message.author.mention}, куда ' + Utility.gender(message.author, 'собрался?', 'собралась?') + \
                    f' {Utility.emote("durka")} \nТебе сидеть в дурке ещё {minutes_left} {Utility.minutes(minutes_left)}! \n')
                return
            else:
                await message.channel.send(f'{message.author.mention}, приказ уже выполнен! \n{user.mention} будет сидеть в дурке ещё {minutes_left} {Utility.minutes(minutes_left)}! \n')
                return
        # Дурка реализована как статус опьянения (hangover). Так как все команды в дурке изменены это ничего не ломает и об этом невозможно узнать
        min_timeout = random.randrange(30, 40)
        durka[user.id].last_drink_time = datetime.datetime.now()
        durka[user.id].set_hangover(min_timeout)
        if user is message.author:
            await message.channel.send(f'{Utility.emote("durka")} увозим {message.author.mention} на {min_timeout} {Utility.minutes(min_timeout)}! \n{Utility.gender(message.author, "Молодой человек", "Девушка")}, пройдёмте... {Utility.emote("durka")}')
        else:    
            await message.channel.send(f'{user.mention}, на Вас поступила жалоба! {Utility.emote("durka")} \nЗа странное поведение увозим Вас на {min_timeout} {Utility.minutes(min_timeout)}!')

    # !выпустить [@юзер] - админская команда, выпускает юзера из дурки
    # если юзер не указан, выпускает автора сообщения
    if message.content.startswith('!выпустить'):
        if len(message.content.split()) == 1:
            user = message.author
        else:
            try:
                user = discord.utils.get(message.guild.members, id=Utility.get_id(message.content.split()[1]))
            except ValueError:
                user = None

        if user is None or user.id not in durka.keys():
            await message.channel.send(f'Таких пациентов не поступало... пока что {Utility.emote("durka")}')
            return

        if durka[user.id].timeout_untill > datetime.datetime.now():
            if Utility.has_permissions(message.author):
                durka[user.id].timeout_untill = datetime.datetime.now() - datetime.timedelta(hours=1) # таймаут в прошлом = нет таймаута
                await message.channel.send(f'Поступил приказ, выпускаем {user.mention} {Utility.emote("durka")}')
            elif len(message.content.split()) > 1 and user.id is not message.author.id:
                if message.author.id not in durka.keys(): 
                    await message.channel.send(f'{message.author.mention}, а может мы лучше Вас заберём? {Utility.emote("durka")}')
                else:
                    await message.channel.send(f'Кажется, пациенты {message.author.mention} и {user.mention} планируют побег! {Utility.emote("monkaSpolice")}')
            else:
                minutes_left = ceil((durka[message.author.id].timeout_untill - datetime.datetime.now()).total_seconds() / 60)
                await message.channel.send(f'{message.author.mention}, куда ' + Utility.gender(message.author, 'собрался?', 'собралась?') + \
                    f' {Utility.emote("durka")} \nТебе сидеть в дурке ещё {minutes_left} {Utility.minutes(minutes_left)}! \n')
        else: # юзера нет в дурке
            await message.channel.send(Utility.gender(user, 'Пациента', 'Пациентку') + f' {user.mention} уже выпустили {Utility.emote("durka")}')

    # !буянить - юзер начинает буянить
    # Бот в зависимости от ситуации действует
    
    if message.content == '!буянить':
        if message.author.id in durka.keys() and durka[message.author.id].timeout_untill > datetime.datetime.now():
            await message.channel.send(f'На вас надета смирительная рубашка, вы не сможете навредить {Utility.emote("durka")}')
        else:
            members = []
            for member in message.guild.members:
                in_durka = (member.id in durka.keys() and durka[member.id].timeout_untill > datetime.datetime.now())
                if member.status is discord.Status.online and member.id != message.author.id and not in_durka:
                    members.append(member)
            await bartender.rage(message.author, random.choice(members), message.channel)

    '''Разное'''
    if message.content == '!head':
        await message.channel.send(f'{message.author.mention}, сегодня ты')
        await message.channel.send(Utility.emote(random.choice(heads)))


    if message.content == '!альпака':
        if message.author.id in durka.keys() and durka[message.author.id].timeout_untill > datetime.datetime.now():
            await message.channel.send(f'альпакА {Utility.emote("durka")}')
        else:
            await message.channel.send(Utility.emote("alpaka"))
            await message.channel.send(f'{Utility.emote("Pepega")} 📣 альпакА')


    if message.content == '!слава':
        if message.channel == Constants.MUSIC_CHANNEL:
            await message.channel.send('!play <https://youtu.be/NluJAtDP2Ow>')
            return
        if message.author.id in durka.keys() and durka[message.author.id].timeout_untill > datetime.datetime.now():
            await message.channel.send(f'Ты что, хочешь чтобы было как на Украине? {Utility.emote("durka")}')
            return
        if message.author.id in Constants.UKR_IDs:
            await message.channel.send(Utility.emote("3Head") + " " + Utility.emote("UKR"))
        else:
            await message.channel.send('Вийди отсюда, розбiйник! Плохо чуеш мене?')

client.run(Constants.TOKEN)
