from abc import ABC, abstractmethod
import math
from areal import constants as cn

class Plant_proto(ABC):
    def __init__(self, field, x, y):
        self.field = field
        self.world = field.world
        self.all_energy = 0
        # координаты экранного пространства,  а не физические
        self.x = x
        self.y = y
        self.sx, self.sy = self.phys_to_screen(x, y)
        self.age = 0
        type(self).COUNT += 1 # глобальный счетчик сущностей
        self.field.counts[self.name] += 1 # счетчик сущностей на клетке
        self.id = cn.global_counter()
        self.field.add_to_new_pool(self)

    @abstractmethod
    def update(self):
        self.age += 1

    def count_down(self):
        type(self).COUNT -= 1
        self.field.counts[self.name] -= 1 # убавляе количество сущностей на клетке
        self.field.add_to_obsolete_pool(self)


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
