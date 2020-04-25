
from areal import constants as cn

from areal.proto import Plant_proto
from areal.rot import Rot
from main import App
print('При имторте в plant', App.CHECKS)

class Plant(Plant_proto):
    LIFETIME = int(cn.PLANT_LIFETIME_YEARS * cn.MONTHS)
    BREED_TIME = int(cn.FRUITING_PERIOD * cn.MONTHS)
    TIME_COEF = 4 / cn.MONTHS  # коэффициент влияющий на скорость роста и питания
    # чем больше скважность, тем более мелкими порциями растение питается
    GROW_UP_PER_IIC = 15 / cn.MONTHS
    ALPHA = 0.1 * GROW_UP_PER_IIC
    BETA = 0.3 * GROW_UP_PER_IIC
    GAMA = 0.5 * GROW_UP_PER_IIC
    EPSILON = 0.3

    header = 'time\tID\tpmalnt coords\tage\tmass\ttotal food consumed\tfood to live\t food to grow\t food ability\tget food\tmass delta\tsoil in field\n'
    p_file = open('plant_table.csv', 'w', encoding='UTF16')
    p_file.write(header)

    def __init__(self,  field, app, sx, sy):
        self.name = 'plant'
        super().__init__(field, app, sx, sy)
        self.mass = cn.SEED_MASS
        self.all_energy = cn.TOTAL_SEED_MASS  # еда, потребленная за всю жизнь
        self.world.plants[self.id] = self
        self.field.plants[self.id] = self


    def count_needs(self):
        self.res_to_live = self.ALPHA * self.mass  # сколько ресурсов нужно просто на поддержание жизни
        self.res_to_grow = self.BETA * (cn.PLANT_MAX_MASS - self.mass)
        self.res_ability = self.GAMA * (1 + self.EPSILON * self.mass)  # возможность добыть еды за ход
        return self.res_to_live, self.res_to_grow, self.res_ability

    def feed(self):
        res_to_live, res_to_grow, res_ability = self.count_needs()
        want =  min(res_to_live + res_to_grow, res_ability)
        self.get = min(want, self.field.soil)
        self.field.soil -= self.get
        self.all_energy += self.get
        self.delta = self.get - res_to_live  # растение может получать меньше, чем тратит на жизнь
        self.color = cn.SICK_PLANT_COLOR if self.delta < 0 else cn.FRESH_PLANT_COLOR
        self.mass += self.delta
        if self.mass < 0.5:  # как только масса понижается до минимума, растение гибнет от голода
            self.die()


    def update(self):
        if self.age == self.LIFETIME:
            self.die()
        else:
            if self.world.global_time % self.BREED_TIME == 0 and self.mass > 0.95 * cn.PLANT_MAX_MASS:
                self.world.to_breed.append(self)  # встает в очередь на размножение
            self.feed()
            self.age += 1
            self.world.itemconfigure(self.id, fill=self.color)

    def split_mass(self):
        """
        Вызывается при размножении. Уменьшает массу растения нм амссу семечка.
        Возвращает массу семечка
        :return: seed_mass
        """
        self.mass -= cn.TOTAL_SEED_MASS
        self.all_energy -= cn.TOTAL_SEED_MASS
        return cn.TOTAL_SEED_MASS

    def die(self, string=None):
        if string is not None:
            print("DIES of ", string)
        self.del_img()
        Rot(self.field, self.app, self.sx, self.sy, self.all_energy)
        del self.world.plants[self.id]
        del self.field.plants[self.id]

    def info(self):
        p1 = str(self.world.global_time)
        p2 = str(self.id)
        plant_coords = '[%2d][%2d]' % (self.field.row, self.field.col)
        p3 = str(self.age)
        p4 = '%4.1f' % self.mass
        p5 = '%5.1f' % self.all_energy
        p6 = '%4.1f' % self.res_to_live
        p7 = '%4.1f' % self.res_to_grow
        p8 = '%4.1f' % self.res_ability
        p9 = '%4.1f' % self.get
        p10 = '%4.1f' % self.delta
        soil = '%7.1f\n' % self.field.soil
        plant_string = '\t'.join([p1, p2, plant_coords, p3, p4, p5, p6, p7, p8, p9, p10, soil]).replace('.', ',')
        self.p_file.write(plant_string)

    def string_info(self):
        s = '----------\n'
        s += 'ID = %d\t' %self.id
        s += 'age = %d\t' % self.age
        s += 'mass = %4.1f\t' % self.mass
        s += 'consumed = %5.1f\n' % self.all_energy
        s += 'to live = %4.1f\t' % self.res_to_live
        s += 'to grow = %4.1f\t' % self.res_to_grow
        s += 'abil = %4.1f\t' % self.res_ability
        s += 'get = %4.1f\t' %self.get
        s += 'mass up = %4.1f\n'% self.delta
        return  s


