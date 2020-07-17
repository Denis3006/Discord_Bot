import datetime
import random

import discord

import src.Constants as Constants
import src.Utility as Utility
from src.Alcoholic import Alcoholic

class Bartender:
    def __init__(self):
        self.special = False  # флаг для специальных ивентов (пока что один)
        self.random_drinks = {  # словарь напитков в баре формата "название: (реплика, алко)", где алко - степень опьянения от напитка
            'спирт':                (f', порция чистого спирта {Utility.emote("Pepega")} \nНадеюсь ты не помрёшь {Utility.emote("LULW")}', 50),
            'водка':                (f', Ваша водка {Utility.emote("PepeHappy")}', 20),
            'виски':                (f', Ваш виски {Utility.emote("PepeHappy")} {Utility.emote("tumbler_glass")}', 20),
            'ром':                  (f', Ваш ром {Utility.emote("PepeHappy")} {Utility.emote("tumbler_glass")}', 20),
            'коньяк':               (f', Ваш коньячок {Utility.emote("PepeHappy")} {Utility.emote("tumbler_glass")}', 20),
            'виски кола':           (f', Ваш коктейль "Виски кола" {Utility.emote("PepeHappy")}', 16),
            'ром кола':             (f', Ваш коктейль "Ром кола" {Utility.emote("PepeHappy")}', 16),
            'джин тоник':           (f', Ваш коктейль "Джин тоник" {Utility.emote("PepeHappy")}', 14),
            'водка с redbull':      (f', Ваш коктейль "Водка с Redbull" {Utility.emote("PepeHappy")}', 16),
            'кровавая мэри':        (f', Ваш коктейль "Кровавая Мэри" {Utility.emote("PepeHappy")}', 13),
            'секс на пляже':        (f', Ваш коктейль "Секс на пляже" {Utility.emote("PepeHappy")}', 13),
            'текила санрайз':       (f', Ваш коктейль "Текила Санрайз" {Utility.emote("PepeHappy")}', 15),
            'пина колада':          (f', Ваш коктейль "Пина Колада" {Utility.emote("PepeHappy")}', 13),
            'белый русский':        (f', Ваш коктейль "Белый русский" {Utility.emote("PepeHappy")}', 15),
            'дайкири':              (f', Ваш коктейль "Дайкири" {Utility.emote("PepeHappy")}', 14),
            'космополитен':         (f', Ваш коктейль "Космополитен" {Utility.emote("PepeHappy")}', 14),
            'егерь-энерджи':        (f', Ваш коктейль "Егерь-энерджи" {Utility.emote("PepeHappy")}', 16),
            'лонг айленд':          (f', Ваш коктейль "Лонг Айленд" {Utility.emote("PepeHappy")}', 14),
            'мохито':               (f', Ваш коктейль "Мохито" {Utility.emote("PepeHappy")}', 15),
            'портвейн':             (f', Ваш Портвейн 777 {Utility.emote("PepeHappy")} {Utility.emote("tumbler_glass")}', 7),
            'красное вино':         (f', Ваш бокал красного винишка {Utility.emote("PepeHappy")} {Utility.emote("wine_glass")}', 6),
            'белое вино':           (f', Ваш бокал белого винишка {Utility.emote("PepeHappy")}', 6),
            'розовое вино':         (f', Ваш бокал розового чилийского винишка {Utility.emote("PepeHappy")}', 6),
            'шампанское':           (f', Ваш шампусик {Utility.emote("PepeHappy")} {Utility.emote("champagne_glass")}', 5),
            'сидр':                 (f', Ваш сидр {Utility.emote("PepeHappy")}', 5),
            'пиво':                 (f', Ваш пивасик {Utility.emote("PepeHappy")} {Utility.emote("beer")}', 5),
            'водичка':              (f', Ваша водичка {Utility.emote("cup_with_straw")} На сегодня хватит {Utility.emote("monkaSpolice")}', -10),
            'квас':                 (f', Ваш холодный квас {Utility.emote("MHM")}', 1),
            'мадера':               (f', Ваше португальское крепленое вино мадера c кусочком кекса в прикуску! {Utility.emote("pepeOK")}', 10),
            'херес':                (f', Ваш испанский херес! Почувствуйте эти сладкие нотки винограда', 10),
            'саке':                 (f', Ваш японский саке! Никогда не думал, что забродивший рис такой вкусный {Utility.emote("PepeHappy")}', 8),
            'абсент':               (f', Ваш крепчайший абсент! Решил напиться в стельку - абсент - твой кандидат! {Utility.emote("wlgDeer")}', 40),
            'аквавит':              (f', Ваш картофельный аквавит! Норвежская "Вода жизни" из картофеля {Utility.emote("PepoFlex")}', 17),
            'граппа':               (f', Ваша итальянская граппа! Дешево и со вкусом', 20),
            'итальянская жена':     (f', Ваша итальянска жена приехала! Надеюсь, вы ей не изменяли с другими напитками', 13),
            'кловер клаб':          (f', Ваш кловер клаб! Джин, малина, лайм и белок перепелиного яйца... Стоп, а яйцо точно должно быть? {Utility.emote("3Head")}', 13),
            'апероль шприц':        (f', Ваш апероль шприц! Самый популярный коктейль Средиземного моря теперь в ваших руках {Utility.emote("tropical_drink")}', 10),
            'молочный удар':        (f', Ваш молочный удар! Вы думали, это молоко? Нет, это оно - виски', 22),
            'ву-ву':                (f', Ваш ву-ву! Главное, чтобы потом не было бо-бо', 17),
            'баунти мартини':       (f', Ваш баунти мартини! По сути, клубнично-кокосовый милкшейк, вкусно и легко', 9),
            'греческая смоковница': (f', Ваша смоковница с инжиром! Выпиваешь шот, затем закусываешь инжиром - ничего сложного!', 19),
            'россини':              (f', Ваш россини! Легкий коктейль из клубничной пюрешки и просекко {Utility.emote("strawberry")}', 12)
            }

        self.drinks = {
            'хугарден' :  (f', Ваш тёплый Хугарден {Utility.emote("pepeClown")}', 5),
            'вода'     :  (f', Ваша вода {Utility.emote("cup_with_straw")}', -10),
            'энергетик':  (f', Ваш энергетик! {Utility.emote("PepeKMS")} \nНе спать! {Utility.emote("pepeRage")}', 0)
            }

        self.coffee = {
            'американо'              : (f', Ваш американо {Utility.emote("coffee")}', 0),
            'капучино'               : (f', Ваш капучино {Utility.emote("coffee")}', 0),
            'латте'                  : (f', Ваш латте {Utility.emote("coffee")}', 0),
            'арахисовый латте'       : (f', Ваш арахисовый латте {Utility.emote("PepeHappy")} {Utility.emote("coffee")}', 0),
            'моккачино'              : (f', Ваш моккачино {Utility.emote("coffee")}', 0),
            'флет уайт'              : (f', Ваш флет уайт {Utility.emote("coffee")}', 0),
            'маккиато'               : (f', Ваш маккиато {Utility.emote("coffee")}', 0),
            'дынный раф'             : (f', Ваш дынный раф {Utility.emote("PepeHappy")} {Utility.emote("coffee")}', 0),
            'цитрусовый раф'         : (f', Ваш цитрусовый  раф {Utility.emote("PepeHappy")} {Utility.emote("coffee")}', 0),
            'шоколадный раф'         : (f', Ваш шоколадный раф {Utility.emote("PepeHappy")} {Utility.emote("coffee")}', 0),
            'ежевичный раф'          : (f', Ваш ежевичный раф {Utility.emote("PepeHappy")} {Utility.emote("coffee")}', 0),
            'грушевый раф'           : (f', Ваш грушевый раф {Utility.emote("PepeHappy")} {Utility.emote("coffee")}', 0),
            'карамель маккиато'      : (f', Ваш сладенький карамель маккиато {Utility.emote("PepeHappy")}', 0),
            'просто кофе'            : (f', Ваш самый обчыный кофе {Utility.emote("4Head")}', 0),
            'эспрессо'               : (f', Ваше экспрессо {Utility.emote("3Head")}', 0),
            'колд брю'               : (f', Ваш прохладительный колд брю {Utility.emote("ice_cube")}', 0),
            'карамельный фраппучино' : (f', Ваш карамельный фраппучино со взбитыми сливками {Utility.emote("PepeHappy")}', 0),
            'эспрессо фраппучино'    : (f', Ваш эспрессо фраппучино: молоко с молотым льдом и шотом эспрессо {Utility.emote("MHM")}', 0),
            'мокка фраппучино'       : (f', Ваш мокка фраппучино {Utility.emote("coffee")}', 0),
            'ванильный фраппучино'   : (f', Ваш ванильный фраппучино {Utility.emote("PepeHappy")} {Utility.emote("coffee")}', 0),
            'шоколадный фраппучино'  : (f', Ваш сладенький шоколадный фраппучино {Utility.emote("PepeHappy")} {Utility.emote("coffee")}', 0),
            'руссиано'               : (f', Ваш патриотический руссиано {Utility.emote("4Head")}', 0)
            }

        self.tea = {
            'чёрный чай'  : (f', Ваш чёрный чай {Utility.emote("tea")}', 0),
            'розовый чай' : (f', Ваш розовый чай {Utility.emote("PepeHappy")} {Utility.emote("tea")}', 0),
            'зелёный чай' : (f', Ваш зелёный чай {Utility.emote("tea")}', 0),
            'белый чай'   : (f', Ваш белый чай {Utility.emote("PepeHappy")} {Utility.emote("tea")}', 0),
            'пуэр'        : (f', Ваш пуэр {Utility.emote("tea")}', 0),
            'дарджилинг'  : (f', Ваш дар... даржилинх {Utility.emote("3Head")}', 0),
            'красный чай' : (f', Ваш красный чай {Utility.emote("tea")}', 0),
            'мате'        : (f', Ваш мате {Utility.emote("mate")}', 0)
            }

        self.compliments = [  # список комплиментов бармена в формате "(реплика для парней, реплика для девушек)"
            (f', Вы такой красивый сегодня! {Utility.emote("pepehype")}', f', Вы такая красивая сегодня! {Utility.emote("peepoPANTIES")}'),
            (f', выглядишь потрясающе! {Utility.emote("gaygasm")}', f', выглядишь потрясающе! {Utility.emote("PepeHappy")}'),
            (f', отличный прикид! {Utility.emote("pepeOK")}', f', какие у тебя красивые... глаза! {Utility.emote("monkaS")}'),
            (f', Вам привет от обаятельной девушки за дальним столиком {Utility.emote("pepehype")}', f', Вам привет от обаятельного парня за дальним столиком {Utility.emote("pepehype")}')
            ]

        self.thanks_replies = [  # список ответов на благодарности
            f', не за что! {Utility.emote("pepeOK")}',
            f', всегда пожалуйста! {Utility.emote("pepeOK")}',
            f', обращайся! {Utility.emote("PepeHappy")}',
            f', рад помочь! {Utility.emote("pepehype")}',
            f', обращайся, всегда рад помочь! {Utility.emote("PepeHappy")}',
            f', не стоит благодарности! {Utility.emote("pepeOK")}',
            f', Вам спасибо! {Utility.emote("PepeHappy")}',
            f', без проблем! {Utility.emote("Pepechill")}',
            f', рад быть полезным! {Utility.emote("pepehype")}',
            f', любой каприз за Ваши деньги {Utility.emote("pepeDavidStar")}',
            f', всегда рад стараться! {Utility.emote("pepeOK")}',
            f', это просто моя работа {Utility.emote("MHM")}',
            f', пожалуйста, конечно, но вы кто? {Utility.emote("Bored")}'
            ]

        self.rage_replies = [ # список действий, которые может сделать игрок, когда буянит
            ' берет стакан и кидает его в случайного посетителя. Он летит в {}.',
            ' разбрасывает окурки из пепельницы. Окурок попадает на одежду {}',
            ' затевает драку с {} и побеждает',
            ' затевает драку с {} и проигрывает',
            ' выплескивает ближайший напиток в {}',
            ' плюет {} в лицо',
            ' отнимает {} у {} и выпивает этот напиток залпом.',
            ' берет бутылку в руки и делает из неё розочку. {} в опасности',
            ' начинает громко орать на {}',
            ' начинает спорить с {}',
            ' спихивает со стула {}',
            ' обзывает {} 1Head-ом ' + Utility.emote("1Head"),
            ' танцует на столе с {}',
            ' показывает средний палец {}',
            ' называет {} уродом ' + Utility.emote("YROD")
        ]

        self.rage_throw_glass = [
            'Стакан попадает в голову. Несите повязку и анальгин!',
            'Стакан попадает в руку. Держать напитки становится труднее.',
            'Стакан попадает в живот. Пивное пузо {} все защитило.',
            'Стакан попадает в ногу. Пора делать деревянную ногу и пить грог.',
            'Стакан попадает в сосочек.'
        ]


    async def reply_thanks(self, user, channel):
        await channel.send(f'{user.mention}{random.choice(self.thanks_replies)}')


    async def check_alco(self, user, channel):
        alcoholic = Alcoholic(user.id)
        if alcoholic.alco_test() == 0:
            alcoholic.reset()
        elif not alcoholic.hangover:  # обновляет значение восстановления, если юзер не полностью пьян
            alcoholic.recover()
        if alcoholic.timeout_mins_left == 0 and alcoholic.hangover is True:
            # тайамут из-за полного опьянения был, но прошёл. обнуляем значения, и поднимаем процент оставшегося опьянения до рандомного значения
            alcoholic.set_alco(random.randrange(30, 70))
        alco_test = alcoholic.alco_test()
        if alco_test == 100:
            await channel.send(random.choice(\
                [f'{user.mention}, выглядишь на все :100: {Utility.emote("MonkaChrist")}', \
                f'{user.mention}, ты {Utility.gender(user, "пьян", "пьяна")} на 100% {Utility.emote("Pepechill")} \nИди проспись! {Utility.emote("MHM")}']))
        else:
            await channel.send(f'{user.mention}, ты {Utility.gender(user, "пьян", "пьяна")} на {alcoholic.alco_test()}% {Utility.emote("Pepechill")}')


    # Юзер начинает буянить в баре
    async def rage(self, user, channel, rage_to):
        alcoholic = Alcoholic(user.id)
        if rage_to.id == Constants.ZAKHOZHKA_ID:
            await channel.send(f"{rage_to.mention} получает ладошкой по лбу от {user.mention}")
            return
        if alcoholic.timeout_mins_left() > 0:
            await channel.send(f"{user.mention}, ты слишком пьян для этого, проспись!")
            return
        else:
            alcoholic.recover()
        if alcoholic.alco_test() >= 50:
            action = random.choice(self.rage_replies)
            await self.check_rage_situations(user, channel, action, rage_to)
        else:
            await channel.send(f'Вы же не настолько пьяны, чтобы делать это? {Utility.emote("monkaSpolice")}')


    async def check_rage_situations(self, user, channel, action, rage_to):
        alcoholic = Alcoholic(user.id)
        if action == self.rage_replies[0]:
            await channel.send(f'{user.mention}{action}'.format(rage_to.mention))
            if bool(random.getrandbits(1)):
                throw = random.choice(self.rage_throw_glass)
                if throw == self.rage_throw_glass[4]:
                    await channel.send(f'{throw} {rage_to.mention} {Utility.gender(rage_to, "возбудился", "возбудилась")}')
                else:
                    await channel.send(f'{throw}'.format(rage_to.mention))
            else:
                await channel.send(f'Вы промахнулись, стакан вдребезги разбился о стену')
        elif action == self.rage_replies[6]:
            drink_name = random.choice(list(self.random_drinks.keys()))
            drink = self.random_drinks[drink_name]
            alcoholic.set_alco(alcoholic.alco_test() + drink[1])
            await channel.send(f'{user.mention}{action}'.format(drink_name, rage_to.mention))
        else:
            await channel.send(f'{user.mention}{action}'.format(rage_to.mention))


    # наливает напиток юзеру (меняет степень опьянения; даёт таймаут, если степень опьянения >=100; выдаёт реплику)
    async def give_drink(self, user, channel, drink_name=None, gift_giver=None, give_compliment=None):
        alcoholic = Alcoholic(user.id)
        if alcoholic.alco_test() == 0:
            alcoholic.reset()
        elif not alcoholic.hangover:
            alcoholic.recover()

        minutes_left = alcoholic.timeout_mins_left()
        if minutes_left > 0:  # таймаут уже есть
            if gift_giver:
                await channel.send(f'{gift_giver.mention}, не трогай {user.mention}, {Utility.gender(user, "ему", "ей")} бы проспаться.' +\
                f' {Utility.emote("Pepechill")} Попробуй угостить через {str(minutes_left)} {Utility.minutes(minutes_left)}.')
            else:
                await channel.send(f'{user.mention}, тебе бы проспаться. {Utility.emote("Pepechill")} Приходи через {minutes_left} {Utility.minutes(minutes_left)}.')
            return
        elif alcoholic.hangover:  # таймаут был, но прошёл
            alcoholic.set_alco(random.randrange(30, 70))

        if not drink_name:
            if discord.utils.get(Constants.GUILD.roles, name='Хугарднутый') in user.roles and self.special and gift_giver is None:
                drink = self.drinks['хугарден']
            else:
                drink = random.choice(list(self.random_drinks.values()))
        else:
            drink = self.get_drink(drink_name)
        if not drink:
            if gift_giver:
                await channel.send(f'Простите, {gift_giver.mention}, такого в нашем баре не наливают {Utility.emote("FeelsBanMan")}')
            else:
                await channel.send(f'Простите, {user.mention}, такого в нашем баре не наливают {Utility.emote("FeelsBanMan")}')
            return
            
        success = random.randrange(50) != 0  # шанс на успех команды
        if success:
            alcoholic.set_alco(alcoholic.alco_test() + drink[1])

        if gift_giver:
            await channel.send(phrase_for_gifted_drink(success, drink, gift_giver, user))
        else:
            await channel.send(phrase_for_nongifted_drink(success, drink, user))

        if give_compliment is None:
            give_compliment = (random.randrange(10) == 0)
        if give_compliment:
            compliment = self.choose_compliment(user)
            await channel.send(user.mention + compliment)


    def get_drink(self, drink_name: str):
        if drink_name == 'чай':
            return random.choice(list(self.tea.values()))
        elif drink_name == 'кофе':
            return random.choice(list(self.coffee.values()))
        elif drink_name == 'вино':
            return self.random_drinks[random.choice([key for key in self.random_drinks.keys() if drink_name in key])]
        elif drink_name == 'раф' or drink_name == 'фраппучино':
            return self.coffee[random.choice([key for key in self.coffee.keys() if drink_name in key])]
        elif drink_name.lower() in self.random_drinks.keys():
            return self.random_drinks[drink_name.lower()]
        elif drink_name.lower() in self.drinks.keys():
            return self.drinks[drink_name.lower()]
        elif drink_name.lower() in self.tea.keys():
            return self.tea[drink_name.lower()]
        elif drink_name.lower() in self.coffee.keys():
            return self.coffee[drink_name.lower()]
        else:
            return None
    

    def choose_compliment(self, user):
        compliment_nr = random.randrange(len(self.compliments))
        if Constants.FEMALE_ROLE in user.roles:
            return self.compliments[compliment_nr][1]
        else:
            if compliment_nr == 3 and Constants.BARTENDER_ROLE in user.roles:
                return self.compliments[compliment_nr][1]
            else:
                return self.compliments[compliment_nr][0]


def phrase_for_gifted_drink(success, drink, gift_giver, gift_reciever):
    if not success:
        return random.choice(
            [f'Ой, я кажется разлил напиток от {gift_giver.mention} для {gift_reciever.mention}. Прошу прощения {Utility.emote("FeelsBanMan")}',
             f'{gift_reciever.mention}, Вас ' + Utility.gender(gift_giver, 'хотел угостить', 'хотела угостить') + f' {gift_giver.mention}! {Utility.emote("PepeHappy")}' +
            f'\nПростите, я задумался и выпил Ваш напиток. Было вкусно {Utility.emote("pepeClown")}'])
    else:
        return f'{gift_reciever.mention}, Вас ' + Utility.gender(gift_giver, 'угостил', 'угостила') + f' {gift_giver.mention}! {Utility.emote("PepeHappy")} Держите{drink[0]}'


def phrase_for_nongifted_drink(success, drink, user):
    if not success:
        return random.choice(
            [f'Ой, я кажется разлил напиток для {user.mention}. Прошу прощения {Utility.emote("FeelsBadMan")}',
            f'{user.mention}, простите, я заработался и не заметил, как выпил Ваш напиток {Utility.emote("monkaS")}'])
    elif random.randrange(10) == 0:
        return f'На этот раз за счёт заведения, {user.mention}{drink[0]}'
    else:
        return f'Пожалуйста, {user.mention}{drink[0]}'
