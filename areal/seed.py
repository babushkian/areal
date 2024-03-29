from areal import field as fd # класс загружается только при таком импорте, не знаю почему
from areal import constants as cn
from areal.proto import Plant_proto
from areal.plant import Plant


class Seed(Plant_proto):
    COUNT = 0
    def __init__(self, field,  x, y, seed_mass): # добавлю параметры позже
        # в будущем у зерна надо сделать регулируемый запас питательных веществ, чтобы его жизнь
        # зависела от этого запаса. А сам запас определялся геномом растений
        self.name = 'seed'
        super().__init__(field, x, y)
        self.all_energy = seed_mass
        self.food = cn.SEED_HIDDEN_MASS
        self.grow_up_age = cn.SEED_PROHIBITED_GROW_UP * cn.MONTHS
        self.field.seeds[self.id] = self

    def update_old(self):
        super().update()
        if self.age > cn.SEED_LIFE * cn.MONTHS:
            self.become_rot()
        else:
            if self.field.soil >= cn.SEED_GROW_UP_CONDITION and self.age >= self.grow_up_age:
                self.grow_up()

    def update(self):
        super().update()
        self.food -= min(self.food, cn.SEED_FEED)
        if self.food == 0:
            self.become_rot()
        else:
            if self.field.soil >= cn.SEED_GROW_UP_CONDITION and self.age >= self.grow_up_age:
                self.grow_up()


    def grow_up(self):
        if len(self.field.plants) < fd.Field.MAX_PLANTS_IN_FIELD:
            Plant(self.field,  self.x, self.y, cn.SEED_MASS, self.food)
            self.field.rot_mass += cn.SEED_HIDDEN_MASS - self.food
            self.destroy_seed()
        else:
            self.become_rot()

    def become_rot(self):
        self.field.rot_mass += self.all_energy
        self.destroy_seed()

    def destroy_seed(self):
        self.count_down()
        del self.field.seeds[self.id]

