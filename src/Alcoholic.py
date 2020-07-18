import datetime
import random
from math import ceil

import src.psql as psql


def clip(x, x_min, x_max):
    return max(x_min, min(x, x_max))

class Alcoholic:
    def __init__(self, member_id):
        self.id = member_id
        self.recovery_rate = 1/6    # скорость восстановления степени опьянения со временем (алко/мин)
        query_result = psql.get_alcogolic_data(self.id)
        self.alco_percent = query_result['alco_percent']            # степень опьянения в процентах от 0 до 100
        # метка времени, до которого был выдан таймаут (таймаут в прошлом = нет таймаута)
        self.hangover_untill = query_result['hangover_untill']
        self.last_drink_time = query_result['last_drink_time']  # метка времени последнего напитка
        # статус полного опьянения = таймаута. станет True, если процент опьянения дойдёт до 100
        self.hangover = query_result['hangover']
        self.in_durka_untill = query_result['in_durka_untill']
        self.data_changed = False
        self.recover()

    def __del__(self):
        if self.data_changed:
            psql.upload_alcoholic_data(self.id,
                                       {'alco_percent': self.alco_percent,
                                        'hangover': self.hangover,
                                        'hangover_untill': f"'{str(self.hangover_untill)}'",
                                        'last_drink_time': f"'{str(self.last_drink_time)}'",
                                        'in_durka_untill': f"'{str(self.in_durka_untill)}'"})

    # выдаёт процент опьянения с учётом восстановления со временем
    def alco_test(self) -> int:
        if not self.hangover:
            self.recover()
        return clip(self.alco_percent - self.recovered_percent, 0, 100)

    # обновляет значение восстановления опьянения со временем
    def recover(self):
        self.recovered_percent = max(
            0, int((datetime.datetime.now() - self.last_drink_time).total_seconds() // 60 * self.recovery_rate))

    # обнуляет степень опьянения и восстановление
    def reset(self):
        self.alco_percent = 0
        self.recovered_percent = 0
        self.hangover = self.hangover_untill > datetime.datetime.now()
        self.data_changed = True

    # выдаёт таймаут на mins минут
    def set_hangover(self, mins):
        self.hangover = True
        self.hangover_untill = self.last_drink_time + datetime.timedelta(minutes=mins)
        self.data_changed = True

    def set_alco(self, new_alco_percent):
        self.reset()
        self.last_drink_time = datetime.datetime.now()  # изменение степени опьянения засчитывается как напиток
        self.alco_percent = clip(new_alco_percent, 0, 100)
        if self.alco_test() == 100:
            self.set_hangover(random.randrange(20, 40))
        self.data_changed = True

    def timeout_mins_left(self) -> int:
        return max(0, ceil((self.hangover_untill - datetime.datetime.now()).total_seconds() / 60))

    def remove_timeout(self):
        self.hangover_untill = datetime.datetime.now() - datetime.timedelta(hours=1)  # таймаут в прошлом = нет таймаута
        self.data_changed = True

    def durka_mins_left(self) -> int:
        return max(0, ceil((self.in_durka_untill - datetime.datetime.now()).total_seconds() / 60))

    def in_durka(self) -> bool:
        return self.durka_mins_left() > 0

    def set_durka_timeout(self, mins: int):
        self.in_durka_untill = datetime.datetime.now() + datetime.timedelta(minutes=mins)
        self.data_changed = True

    def remove_durka_timeout(self):
        self.in_durka_untill = datetime.datetime.now() - datetime.timedelta(hours=1)
        self.data_changed = True
