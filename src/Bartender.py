import datetime
import random
from math import ceil

import src.Constants as Constants
import src.Utility as Utility
from src.Alcoholic import Alcoholic


class Bartender:
    def __init__(self):
        self.alcoholics = dict()  # словарь юзеров в баре
        self.special = False  # флаг для специальных ивентов (пока что один)
        self.drinks = {  # словарь напитков в баре формата "название: (реплика, алко)", где алко - степень опьянения от напитка
            'спирт':                (f', порция чистого спирта {Utility.emote("Pepega")} \nНадеюсь ты не помрёшь {Utility.emote("LULW")}', 50),
            'водка':                (f', Ваша водка {Utility.emote("PepeHappy")}', 20),
            'виски':                (f', Ваш виски {Utility.emote("PepeHappy")} \U0001F943', 20),
            'ром':                  (f', Ваш ром {Utility.emote("PepeHappy")} \U0001F943', 20),
            'коньяк':               (f', Ваш коньячок {Utility.emote("PepeHappy")} \U0001F943', 20),
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
            'портвейн':             (f', Ваш Портвейн 777 {Utility.emote("PepeHappy")} \U0001F943', 7),
            'красное вино':         (f', Ваш бокал красного винишка {Utility.emote("PepeHappy")} \U0001F377', 6),
            'белое вино':           (f', Ваш бокал белого винишка {Utility.emote("PepeHappy")}', 6),
            'розовое вино':         (f', Ваш бокал розового чилийского винишка {Utility.emote("PepeHappy")}', 6),
            'шампанское':           (f', Ваш шампусик {Utility.emote("PepeHappy")} \U0001F942', 5),
            'сидр':                 (f', Ваш сидр {Utility.emote("PepeHappy")}', 5),
            'пиво':                 (f', Ваш пивасик {Utility.emote("PepeHappy")} \U0001F37A', 5),
            'водичка':              (f', Ваша водичка \U0001F964 На сегодня хватит {Utility.emote("monkaSpolice")}', -10),
            'квас':                 (f', Ваш холодный квас {Utility.emote("MHM")}', 1),
            'вода':                 (f', Ваша вода \U0001F964', -10),
            'энергетик':            (f', Ваш энергетик! {Utility.emote("PepeKMS")} \nНе спать! {Utility.emote("pepeRage")}', 0),
            'мадера':               (f', Ваше португальское крепленое вино мадера c кусочком кекса в прикуску! {Utility.emote("pepeOK")}', 10),
            'херес':                (f', Ваш испанский херес! Почувствуйте эти сладкие нотки винограда', 10),
            'саке':                 (f', Ваш японский саке! Никогда не думал, что забродивший рис такой вкусный {Utility.emote("PepeHappy")}', 8),
            'абсент':               (f', Ваш крепчайший абсент! Решил напиться в стельку - абсент - твой кандидат! {Utility.emote("wlgDeer")}', 40),
            'аквавит':              (f', Ваш картофельный аквавит! Норвежская "Вода жизни" из картофеля {Utility.emote("PepoFlex")}', 17),
            'граппа':               (f', Ваша итальянская граппа! Дешево и со вкусом', 20),
            'итальянская жена':     (f', Ваша итальянска жена приехала! Надеюсь, вы ей не изменяли с другими напитками', 13),
            'кловер клаб':          (f', Ваш кловер клаб! Джин, малина, лайм и белок перепелиного яйца... Стоп, а яйцо точно должно быть? {Utility.emote("3Head")}', 13),
            'апероль шприц':        (f', Ваш апероль шприц! Самый популярный коктейль Средиземного моря теперь в ваших руках {Utility.emote("tropical_drink")}', 10),
            'молочный удар':        (f', Ваш молочный удар! Вы думали, это молоко? Нет, это он - виски', 22),
            'ву-ву':                (f', Ваш ву-ву! Главное, чтобы потом не было бо-бо', 17),
            'баунти мартини':       (f', Ваш баунти мартини! По сути, клубнично-кокосовый милкшейк, вкусно и легко', 9),
            'греческая смоковница': (f', Ваша смоковница с инжиром! Выпиваешь шот, затем закусываешь инжиром - ничего сложного!', 19),
            'россини':              (f', Ваш россини! Легкий коктейль из клубничной пюрешки и просекко {Utility.emote("strawberry")}', 12)
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

    async def reply_thanks(self, user, channel):
        await channel.send(f'{user.mention}{random.choice(self.thanks_replies)}')

    # наливает напиток юзеру (меняет степень опьянения; даёт таймаут, если степень опьянения >=100; выдаёт реплику)
    async def give_drink(self, user, channel, drink=None, gift_giver=None, give_compliment=(random.randrange(10) == 0)):
        if user.id not in self.alcoholics.keys():
            self.alcoholics[user.id] = Alcoholic()
        elif self.alcoholics[user.id].alco_test() == 0:
            self.alcoholics[user.id].reset()
        elif not self.alcoholics[user.id].hangover:
            self.alcoholics[user.id].recover()

        if self.alcoholics[user.id].timeout_untill > datetime.datetime.now():  # таймаут уже есть
            minutes_left = ceil((self.alcoholics[user.id].timeout_untill - datetime.datetime.now()).total_seconds() / 60)
            if gift_giver is not None:
                await channel.send(f'{gift_giver.mention}, не трогай {user.mention}, ' + Utility.gender(user, 'ему', 'ей') + f' бы проспаться. {Utility.emote("Pepechill")} Попробуй угостить через {str(minutes_left)} {Utility.minutes(minutes_left)}.')
            else:
                await channel.send(f'{user.mention}, тебе бы проспаться. {Utility.emote("Pepechill")} Приходи через {str(minutes_left)} {Utility.minutes(minutes_left)}.')
            return
        elif self.alcoholics[user.id].hangover is True:  # таймаут был, но прошёл
            self.alcoholics[user.id].reset()
            self.alcoholics[user.id].alco_percent = random.randrange(30, 70)

        if drink is None:
            random_drink = True
            drink = random.choice(list(self.drinks.values())[:-2])  # последние 2 напитка в словаре напитков не могут нарандомится
        elif drink.lower() in self.drinks.keys():
            drink = self.drinks[drink.lower()]
        else:
            if gift_giver is not None:
                await channel.send(f'Простите, {gift_giver.mention}, такого в нашем баре не наливают {Utility.emote("FeelsBanMan")}')
            else:
                await channel.send(f'Простите, {user.mention}, такого в нашем баре не наливают {Utility.emote("FeelsBanMan")}')
            return

        if user.id == Constants.TGEU_ID and self.special and gift_giver is None and random_drink:  # peepoClown ивент
            self.alcoholics[user.id].alco_percent = self.alcoholics[user.id].alco_test() + 5
            self.alcoholics[user.id].recovered_percent = 0
            self.alcoholics[user.id].last_drink_time = datetime.datetime.now()
            self.alcoholics[user.id].alco_percent = Utility.clip(self.alcoholics[user.id].alco_percent, 0, 100)
            await channel.send(f'Пожалуйста, {user.mention}, Ваш тёплый Хугарден {Utility.emote("pepeClown")}')
            return
            
        success = random.randrange(50) != 0  # шанс на успех команды
        if success:
            self.alcoholics[user.id].alco_percent = self.alcoholics[user.id].alco_test() + drink[1]
            self.alcoholics[user.id].recovered_percent = 0
            self.alcoholics[user.id].last_drink_time = datetime.datetime.now()
            self.alcoholics[user.id].alco_percent = Utility.clip(self.alcoholics[user.id].alco_percent, 0, 100)

        if gift_giver is not None:
            if not success:
                await channel.send(random.choice(\
                    [f'Ой, я кажется разлил напиток от {gift_giver.mention} для {user.mention}. Прошу прощения {Utility.emote("FeelsBadMan")}', \
                    f'{user.mention}, Вас ' + Utility.gender(gift_giver, 'хотел угостить', 'хотела угостить') + f' {gift_giver.mention}! {Utility.emote("PepeHappy")}' + \
                    f'\nПростите, я задумался и выпил Ваш напиток. Было вкусно {Utility.emote("pepeClown")}']))
                return
            else:
                await channel.send(f'{user.mention}, Вас ' + Utility.gender(gift_giver, 'угостил', 'угостила') + f' {gift_giver.mention}! {Utility.emote("PepeHappy")} Держите{drink[0]}')
        else:
            if not success:
                await channel.send(random.choice(\
                    [f'Ой, я кажется разлил напиток для {user.mention}. Прошу прощения {Utility.emote("FeelsBadMan")}', \
                    f'{user.mention}, простите, я заработался и не заметил, как выпил Ваш напиток {Utility.emote("monkaS")}']))
                return
            else:
                if random.randrange(10) == 0:
                    await channel.send(f'На этот раз за счёт заведения, {user.mention}{drink[0]}')
                else:
                    await channel.send(f'Пожалуйста, {user.mention}{drink[0]}')
        
        if give_compliment:  # шанс на комплимент
            compliment_nr = random.randrange(len(self.compliments))
            if Constants.FEMALE_ROLE in user.roles:
                compliment = self.compliments[compliment_nr][1]
            else:
                if compliment_nr == 3 and Constants.BARTENDER_ROLE in user.roles:
                    compliment = self.compliments[compliment_nr][1]
                else:
                    compliment = self.compliments[compliment_nr][0]
            await channel.send(user.mention + compliment)
                    
        if self.alcoholics[user.id].alco_percent >= 100 and not self.alcoholics[user.id].hangover:
            # последний напиток опьянил юзера полностью, выдаём таймаут
            self.alcoholics[user.id].alco_percent = 100
            self.alcoholics[user.id].set_hangover(random.randrange(20, 40))
