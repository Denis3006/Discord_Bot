import datetime
from Utility import clip

class Alcoholic:
    def __init__(self):
        self.recovery_rate = 1/6    # скорость восстановления степени опьянения со временем (алко/мин)
        self.alco_percent = 0       # степень опьянения в процентах от 0 до 100 
        self.recovered_percent = 0  # восстановленные проценты опьянения со временем
        self.timeout_untill = datetime.datetime.now() - datetime.timedelta(hours=1)  # метка времени, до которого был выдан таймаут (таймаут в прошлом = нет таймаута)
        self.last_drink_time = datetime.datetime.now()  # метка времени последнего напитка
        self.hangover = False  # статус полного опьянения = таймаута. станет True, если процент опьянения дойдёт до 100

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