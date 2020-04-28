import random
import math
from collections import Counter
from areal.label import CanvasTooltip

from areal import constants as cn
from areal.plant import Plant
from areal.seed import Seed
from areal.rot import Rot

class Field:  # клетка поля
    # максимальное количество растений на клетку, чтобы симуляция не тормозила
    MAX_PLANTS_IN_FIELD = cn.MAX_PLANTS_IN_FIELD
    # физическое расстояние от центра до края клетки  (половина клетки!!, т.к. PHYS_SIZE - половина игрового поля)
    FIELD_GRAPH_TO_PHYS_PROPORTION = cn.PHYS_SIZE / cn.FIELDS_NUMBER_BY_SIDE

    f_file = open('field_info.csv', 'w', encoding='UTF16')
    header = 'global time\tcoordinates\tplants\trot\tseeds\tbiomass\trot mass\tseeds mass\tsoil\ttotal mass\n'
    f_file.write(header)

    def __init__(self, world, row, col, soil = cn.INIT_SOIL):
        self.world = world
        self.app = world.app
        self.row = row
        self.col = col
        self.name = 'field'
        self.tooltip = None
        self.starving = 0
        self.counts = Counter({'plant':0, 'seed':0, 'rot':0})
        self.plants = {} # словарь растений, размещенных на данной клетке; в качестве ключа - id графического объекта
        self.to_breed = [] # растения, готовые к размножению
        self.rot = {} # гниль на клетке
        self.seeds = {} # семена на клетке
        self.seed_mass =0
        self.plant_mass = 0
        self.rot_mass = 0

        self.soil = soil
        # физические координаты поля: его центра и краев
        self.center_x, self.center_y = self.graph_to_phys(row, col)
        self.lu_x = self.center_x - self.FIELD_GRAPH_TO_PHYS_PROPORTION # left-up conner
        self.lu_y = self.center_y + self.FIELD_GRAPH_TO_PHYS_PROPORTION
        self.rd_x = self.center_x + self.FIELD_GRAPH_TO_PHYS_PROPORTION # right-down corner
        self.rd_y = self.center_y - self.FIELD_GRAPH_TO_PHYS_PROPORTION
        cd = cn.FIELD_SIZE_PIXELS # размер клетки в пикселях. Присваивание сделано для сокращения записи
        self.draw =self.app.CHECKS[self.name][1].get()
        if self.draw:
            self.shape = self.world.create_rectangle(cd * row, cd * col,
                                                  cd * row + cd, cd * col + cd,
                                                  width=0, fill='#888888', tags = self.name)
            self.tooltip = CanvasTooltip(self.world, self.shape, text=self.create_tooltip_text())
        self.area = self.spread_area()  # соседние клетки, на которые происходит  распространиение семян


    def spread_area(self):
        area = []
        r_start = self.row - 1
        c_start = self.col - 1
        for r in range(r_start, self.row +2):
            for c in range(c_start, self.col +2):
                if r in range(cn.FIELDS_NUMBER_BY_SIDE) and c in range(cn.FIELDS_NUMBER_BY_SIDE):  # проверяем, чтобы соседи не вылезали за границы игрового поля
                    area.append((r, c))
        return area


    def set_color(self, color=None):
        '''
        присваивает цвет полю. цвет вычисляется в World
        '''
        if self.app.CHECKS[self.name][1].get():
            self.world.itemconfigure(self.shape, fill=color)

    def create_plant(self):
        """
        Вызывается из класса World при размножении расений
        Служит для инициалищзации пастений  вначале симуляции. В дальнейшем не используется,
        растения прорастают из семян
        """
        # определяем координаты новорожденного растения
        # физические координаты
        x = self.lu_x + random.randrange(int(self.rd_x - self.lu_x))
        y = self.rd_y + random.randrange(int(self.lu_y - self.rd_y))
        # экранные координаты
        sx, sy = self.phys_to_screen(x, y)

        if len(self.plants) < self.MAX_PLANTS_IN_FIELD:
            Plant(self, sx, sy)
        else:
            Rot(self, sx, sy, cn.TOTAL_SEED_MASS)

    def create_seed(self, seed_mass):
        # определяем координаты новорожденного растения
        # физические координаты
        x = self.lu_x + random.randrange(int(self.rd_x - self.lu_x))
        y = self.rd_y + random.randrange(int(self.lu_y - self.rd_y))
        # экранные координаты
        sx, sy = self.phys_to_screen(x, y)
        Seed(self, sx, sy, seed_mass)

    def update_rot(self):
        rot_list = list(self.rot)
        for r in rot_list:
            self.rot[r].update_continuous()

    def update_seeds(self):
        seeds_list = list(self.seeds)
        sl = len(seeds_list)
        if sl > 2:
            x = random.randrange(sl)
            y = random.randrange(sl)
            seeds_list[x], seeds_list[y] = seeds_list[y], seeds_list[x]
        for seed in seeds_list:
            self.seeds[seed].update()


    def update_plants(self):
        if self.to_breed:
            self.breed_plants()
        plants_list = list(self.plants)
        pl = len(plants_list)
        if pl > 2:
            x = random.randrange(pl)
            y = random.randrange(pl)
            plants_list[x], plants_list[y] = plants_list[y], plants_list[x]
        for plant in plants_list:
            self.plants[plant].update()

    def breed_plants(self):
        for p in self.to_breed:
            # выбираем случайную клетку в окрестностях, чтобы засеять семя
            l = len(p.field.area)
            row, col = self.get_near_field_coords()
            seed_mass = p.split_mass()
            self.world.create_seed(row, col, seed_mass)
        self.to_breed = []

    def get_near_field_coords(self):
        l = len(self.area)
        return self.area[random.randrange(l)]


    def info(self):
        self.starving = 0
        self.plant_mass = 0
        for p in self.plants:
            self.plant_mass += self.plants[p].all_energy
            if self.plants[p].delta < 0:
                self.starving += 1
        self.rot_mass = 0
        for r in self.rot:
            self.rot_mass += self.rot[r].all_energy
        self.seed_mass =0
        for s in self.seeds:
            self.seed_mass += self.seeds[s].all_energy
        self.write_info()

    def write_info(self):
        p1 = str(self.world.global_time)
        p2 = '[%2d][%2d]' % (self.row, self.col)
        p3 = '%2d' % self.counts['plant']
        p4 = '%2d' % self.counts['rot']
        p4_1 = '%2d' % self.counts['seed']
        p5 = '%6.1f' % self.plant_mass
        p6 = '%6.1f' % self.rot_mass
        p7 = '%6.1f' % self.seed_mass
        soil = '%7.1f' % self.soil
        total_mass = '%7.1f\n' % (self.plant_mass + self.rot_mass + self.seed_mass + self.soil)
        field_string = '\t'.join([p1, p2, p3, p4, p4_1, p5, p6, p7, soil, total_mass]).replace('.', ',')
        self.f_file.write(field_string)


    def create_tooltip_text(self):
        text = f'Калетка: {self.row:02d}x{self.col:02d}\n'
        text += f'Растений: {self.counts["plant"]:4d}({self.plant_mass:6.1f})\n'
        text += f'Семян: {self.counts["seed"]:4d}({self.seed_mass:6.1f})\n'
        text += f'Гнили: {self.counts["rot"]:4d}({self.rot_mass:6.1f})\n'
        text += f'Масса почвы: {self.soil:6.1f}'
        return text
    # в момент, когда графическией элемент удаляется, а подсказка была активирована, подтсказка
    # остается висеть навсегда, потому что не срабатывает обработчик выхода из поля объекта - его нет.


    def update(self):
        if self.draw:
            self.tooltip.text=self.create_tooltip_text()


    @staticmethod
    def phys_to_screen(x, y):
        side = 2 * cn.PHYS_SIZE
        scr_len = cn.FIELDS_NUMBER_BY_SIDE * cn.FIELD_SIZE_PIXELS
        proportion = scr_len / side
        sx = math.floor(x * proportion + scr_len / 2)
        sy = math.floor(scr_len / 2 - y * proportion)
        return sx, sy

    @staticmethod
    def graph_to_phys(row, col):
        side = 2*cn.PHYS_SIZE
        proportion = side/cn.FIELDS_NUMBER_BY_SIDE
        x = (row + .5) *proportion - cn.PHYS_SIZE
        y = cn.PHYS_SIZE - (col + .5) *proportion
        return x, y
