import datetime
import random
from math import ceil

from src.Utility import clip
import src.psql as psql

class Alcoholic:
    def __init__(self, member_id):
        self.id = member_id
        self.recovery_rate = 1/6    # скорость восстановления степени опьянения со временем (алко/мин)
        query_result = psql.get_alcogolic_data(self.id)
        self.alco_percent = query_result['alco_percent']            # степень опьянения в процентах от 0 до 100
        self.recovered_percent = query_result['recovered_percent']  # восстановленные проценты опьянения со временем
        # метка времени, до которого был выдан таймаут (таймаут в прошлом = нет таймаута)
        self.timeout_untill = query_result['timeout_untill'].replace(tzinfo=None)
        self.last_drink_time = query_result['last_drink_time'].replace(tzinfo=None)  # метка времени последнего напитка
        # статус полного опьянения = таймаута. станет True, если процент опьянения дойдёт до 100
        self.hangover = query_result['hangover']


    def __del__(self):
        id = self.id
        alcoholic_dict = self.__dict__
        del alcoholic_dict['id']
        del alcoholic_dict['recovery_rate']
        alcoholic_dict['timeout_untill'] = f"'{str(alcoholic_dict['timeout_untill'])}'"
        alcoholic_dict['last_drink_time'] = f"'{str(alcoholic_dict['last_drink_time'])}'"   
        psql.upload_alcoholic_data(id, alcoholic_dict)


    def retrieve_alcoholic_from_db(self):
        query_result = psql.get_alcogolic_data(self.id)
        self.alco_percent = query_result['alco_percent']
        self.recovered_percent = query_result['recovered_percent']
        self.timeout_untill = query_result['timeout_untill']
        self.last_drink_time = query_result['last_drink_time']
        self.hangover = query_result['hangover']

    # выдаёт процент опьянения с учётом восстановления со временем
    def alco_test(self):
        if not self.hangover:
            self.recover()
        return clip(self.alco_percent - self.recovered_percent, 0, 100)

    # обновляет значение восстановления опьянения со временем
    def recover(self):
        self.recovered_percent = max(0, int((datetime.datetime.now() - self.last_drink_time).total_seconds() // 60 * self.recovery_rate))

    # обнуляет степень опьянения и восстановление
    def reset(self):
        self.alco_percent = 0
        self.recovered_percent = 0
        self.hangover = self.timeout_untill > datetime.datetime.now()

    # выдаёт таймаут на mins минут
    def set_hangover(self, mins):
        self.hangover = True
        self.timeout_untill = self.last_drink_time + datetime.timedelta(minutes=mins)

    def set_alco(self, new_alco_percent):
        self.reset()
        self.last_drink_time = datetime.datetime.now()  # изменение степени опьянения засчитывается как напиток
        self.alco_percent = clip(new_alco_percent, 0, 100)
        if self.alco_test() == 100:
            self.set_hangover(random.randrange(20, 40))

    def timeout_mins_left(self):
        return max(0, ceil((self.timeout_untill - datetime.datetime.now()).total_seconds() / 60))

    def remove_timeout(self):
        self.timeout_untill = datetime.datetime.now() - datetime.timedelta(hours=1) # таймаут в прошлом = нет таймаута
