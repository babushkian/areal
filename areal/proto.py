from abc import ABC, abstractmethod
from areal import constants as cn
from areal.label import CanvasTooltip



class Plant_proto(ABC):
    def __init__(self, field, sx, sy):
        self.world = field.world
        self.app = self.world.app
        self.tooltip = None
        self.all_energy = 0
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
        self.id = cn.global_counter()
        if self.draw:
            self.gid = self.world.create_rectangle(self.sx - size, self.sy - size, self.sx + size, self.sy + size,
                                                  fill=color, width=border, tags =self.name)
            self.tooltip = CanvasTooltip(self.world, self.gid, text=self.create_tooltip_text())



    def create_tooltip_text(self):
        text = f'{self.name} # {self.gid}  age: {self.age} mass: {self.all_energy:4.1f}'
        return text
    # в момент, когда графическией элемент удаляется, а подсказка была активирована, подтсказка
    # остается висеть навсегда, потому что не срабатывает обработчик выхода из поля объекта - его нет.

    @abstractmethod
    def update(self):
        self.age += 1
        if self.draw:
            self.tooltip.text=self.create_tooltip_text()


    def del_img(self):
        if self.draw:
            self.world.delete(self.gid)
            self.tooltip.onLeave()
            del self.tooltip
