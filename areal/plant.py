from areal import constants as cn

from areal.proto import Plant_proto

class Plant(Plant_proto):
    COUNT = 0
    LIFETIME = int(cn.PLANT_LIFETIME_YEARS * cn.MONTHS)
    BREED_TIME = int(cn.FRUITING_PERIOD * cn.MONTHS)
    GROW_UP_PER_TIC = 15 / cn.MONTHS
    ALPHA = 0.1 * GROW_UP_PER_TIC
    BETA = 0.3 * GROW_UP_PER_TIC
    GAMA = 0.5 * GROW_UP_PER_TIC
    EPSILON = 0.3 * GAMA


    def __init__(self,  field, x, y, mass, hidden):
        self.name = 'plant'
        super().__init__(field, x, y)
        self.mass = mass
        # еда, потребленная за всю жизнь. Нужна чтобы при смерти вернуьб всю энергиюв землю.
        self.all_energy = mass + hidden
        self.field.plants[self.id] = self

    def feed(self):
        def count_needs():
            live = self.ALPHA * self.mass  # сколько ресурсов нужно просто на поддержание жизни
            grow = self.BETA * (cn.PLANT_MAX_MASS - self.mass)
            ability = self.GAMA + self.EPSILON * self.mass  # возможность добыть еды за ход
            return live, grow, ability
        self.res_to_live, self.res_to_grow, self.res_ability = count_needs()
        want =  min(self.res_to_live + self.res_to_grow, self.res_ability)
        self.get = min(want, self.field.plant_ration)
        self.field.soil -= self.get
        self.all_energy += self.get
        self.delta = self.get - self.res_to_live  # растение может получать меньше, чем тратит на жизнь
        self.mass += self.delta
        if self.mass < 0.5:  # как только масса понижается до минимума, растение гибнет от голода
            self.die()


    def update(self):
        super().update()
        if self.age == self.LIFETIME:
            self.die()
        else:
            if self.world.global_time % self.BREED_TIME == 0 and self.mass > 0.95 * cn.PLANT_MAX_MASS:
                self.field.to_breed.append(self)  # встает в очередь на размножение
            self.feed()

    def split_mass(self):
        """
        Вызывается при размножении. Уменьшает массу растения на массу семечка.
        Возвращает массу семечка
        """
        self.mass -= cn.TOTAL_SEED_MASS
        self.all_energy -= cn.TOTAL_SEED_MASS
        return cn.TOTAL_SEED_MASS

    def die(self):
        self.count_down()
        self.field.rot_mass += self.all_energy
        del self.field.plants[self.id]

    def info_dict(self):
        out = dict()
        out['time'] = f'{self.world.global_time}'
        out['ID'] = f'{self.id}'
        out['plant coords'] = f'[{self.field.row:2d}][{self.field.col:2d}]'
        out['age'] = str(self.age)
        out['mass'] = f'{self.mass:4.1f}'.replace('.', ',')
        out['total food consumed'] = f'{self.all_energy:5.1f}'.replace('.', ',')
        out['food to live'] = f'{self.res_to_live:4.1f}'.replace('.', ',')
        out['food to grow'] = f'{self.res_to_grow:4.1f}'.replace('.', ',')
        out['food ability'] = f'{self.res_ability:4.1f}'.replace('.', ',')
        out['get food'] = f'{self.get:4.1f}'.replace('.', ',')
        out['mass delta'] = f'{self.delta:4.1f}'.replace('.', ',')
        out['soil in field'] = f'{self.field.soil:7.1f}'.replace('.', ',')
        return out

