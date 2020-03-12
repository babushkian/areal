import random
import math

from areal import world as wd
from areal import plant as pt


class Field:  # клетка поля
    # максимальное количество растений на клетку, чтобы симуляция не тормозила
    MAX_PLANTS_IN_FIELD = 10

    # расстояние от центра клетки до ее границы в физических единицах
    # есть мение, что тут не вполне правильно, надо разобраться
    FIELD_GRAPH_TO_PHYS_PROPORTION =  1
    INIT_SOIL = 200 # количество почвы на клетке
    f_file = open('field_info.csv', 'w', encoding='UTF16')
    header = 'global time\tcoordinates\tplants\trot\tbiomass\trot mass\tsoil\ttotal mass\n'
    f_file.write(header)

    def __init__(self, world, row, col):
        self.world = world
        self.canvas = world.canvas
        self.row = row
        self.col = col
        self.plants = {} # словарь растениц, размещенных на данной клетке; в качестве ключа - id графического объекта
        self.rot = {} # гниль на клетке
        self.seeds = {} # семена на клетке
        self.plant_mass = 0
        self.rot_mass = 0

        self.soil = self.INIT_SOIL
        # физические координаты поля: его центра и краев
        self.center_x, self.center_y = self.graph_to_phys(row, col)
        self.lu_x = self.center_x - self.FIELD_GRAPH_TO_PHYS_PROPORTION # left-up conner
        self.lu_y = self.center_y + self.FIELD_GRAPH_TO_PHYS_PROPORTION
        self.rd_x = self.center_x + self.FIELD_GRAPH_TO_PHYS_PROPORTION # right-down corner
        self.rd_y = self.center_y - self.FIELD_GRAPH_TO_PHYS_PROPORTION
        cd = wd.CHECK_DIM # размер клетки в пикселях. Присваивание сделано для сокращения записи
        self.shape = self.canvas.create_rectangle(cd * row, cd * col,
                                                  cd * row + cd, cd * col + cd,
                                                  width=0, fill='#888888')
        self.area = self.spread_area()  # соседние клетки, на которые происходит  распространиение семян

    @staticmethod
    def init_constants():
        Field.FIELD_GRAPH_TO_PHYS_PROPORTION = wd.DIMENSION / wd.DRAW_DIM
        pt.Plant.init_constants()
        pt.Rot.init_constants()

    def spread_area(self):
        area = []
        r_start = self.row - 1
        c_start = self.col - 1
        for r in range(r_start, self.row +2):
            for c in range(c_start, self.col +2):
                if r in range(wd.DRAW_DIM) and c in range(wd.DRAW_DIM):  # проверяем, чтобы соседи не вылезали за границы игрового поля
                    area.append((r, c))
        return area


    def set_color(self, color=None):
        '''
        присваивает цвет полю. цвет вычисляется в World
        '''
        self.canvas.itemconfigure(self.shape, fill=color)

    def create_plant(self):
        """
        Вызывается из класса World при размножении расений
        будет змененна на create seed
        """
        # определяем координаты новорожденного растения
        # физические координаты
        x = self.lu_x + random.randrange(int(self.rd_x - self.lu_x))
        y = self.rd_y + random.randrange(int(self.lu_y - self.rd_y))
        # экранные координаты
        sx, sy = self.phys_to_screen(x, y)

        if len(self.plants) < self.MAX_PLANTS_IN_FIELD:
            new_plant = pt.Plant(self, sx, sy)
            self.plants[new_plant.id] = new_plant
        else:
            pt.Rot(self, sx, sy)

    def create_seed(self):
        # определяем координаты новорожденного растения
        # физические координаты
        x = self.lu_x + random.randrange(int(self.rd_x - self.lu_x))
        y = self.rd_y + random.randrange(int(self.lu_y - self.rd_y))
        # экранные координаты
        sx, sy = self.phys_to_screen(x, y)

        if len(self.plants) < self.MAX_PLANTS_IN_FIELD:
            new_seed = pt.Seed(self, sx, sy)
            self.seeds[new_seed.id] = new_seed
        else:
            pt.Rot(self, sx, sy)


    def info(self):
        self.plant_mass = 0
        for p in self.plants:
            self.plant_mass += self.plants[p].all_consumed_food
        self.rot_mass = 0
        for r in self.rot:
            self.rot_mass += self.rot[r].mass
        self.write_info()

    def write_info(self):
        p1 = str(self.world.global_time)
        p2 = '[%2d][%2d]' % (self.row, self.col)
        p3 = '%2d' % len(self.plants)
        p4 = '%2d' % len(self.rot)
        p5 = '%6.1f' % self.plant_mass
        p6 = '%6.1f' % self.rot_mass
        soil = '%7.1f' % self.soil
        total_mass = '%7.1f\n' % (self.plant_mass + self.rot_mass + self.soil)
        field_string = '\t'.join([p1, p2, p3, p4, p5, p6, soil, total_mass]).replace('.', ',')
        self.f_file.write(field_string)

    @staticmethod
    def phys_to_screen(x, y):
        side = 2 * wd.DIMENSION
        scr_len = wd.DRAW_DIM * wd.CHECK_DIM
        proportion = scr_len / side
        sx = math.floor(x * proportion + scr_len / 2)
        sy = math.floor(scr_len / 2 - y * proportion)
        return sx, sy

    @staticmethod
    def graph_to_phys(row, col):
        side = 2*wd.DIMENSION
        proportion = side/wd.DRAW_DIM
        x = (row + .5) *proportion - wd.DIMENSION
        y = wd.DIMENSION - (col + .5) *proportion
        return x, y
