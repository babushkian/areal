from abc import ABC
from areal import constants as cn
from main import App
print('При имторте в прототип', App.CHECKS)
class Plant_proto(ABC):
    def __init__(self, field, app, sx, sy):
        self.world = field.world
        self.app = app
        self.field = field
        # координаты экранного пространства,  а не физические
        self.sx = sx
        self.sy = sy
        self.age = 0
        # в наследуемом классе определяется параметр name, который служит ключом для словарей насроек
        # и тегом для объектов на холсте
        self.draw =  self.app.CHECKS[self.name][1].get()
        self.create_img(**cn.DRAW_PARAMS[self.name])


    def create_img(self, size, color, border):
        if self.draw:
            self.id = self.world.create_rectangle(self.sx - size, self.sy - size, self.sx + size, self.sy + size,
                                                  fill=color, width=border, tags =self.name)
        else:
            self.id = cn.global_counter()

    def del_img(self):
        if self.draw:
            self.world.delete(self.id)
