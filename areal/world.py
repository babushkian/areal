from areal import constants as cn
from areal import weather
from areal.field import Field
from areal.plant import Plant
from areal.seed import Seed
from areal.rot import Rot

class World():
    def __init__(self):
        # создаем пустое игровое поле
        self.fields = dict() # в словаре содержатся объекты клеток; ключ - id клетки
        self.season_time = 0
        self.global_time = 0
        self.years = 0
        self.weather = weather.Weather()
        self.drop_changed_objects() # сбрасываем словарь self.change_scene

    def init_sim(self):
        Plant.COUNT = 0
        Seed.COUNT = 0
        Rot.COUNT = 0
        self.create_fields()
        self.plant_setup_3()
        self.gather_changed_objects()

    def update(self):
        self.update_fields()
        self.update_objects()

    def debug_obj_count(self):
        print(f'pl:{Plant.COUNT} se:{Seed.COUNT}  ro:{Rot.COUNT}')

    def time_pass(self):
        self.years = self.global_time // cn.MONTHS # не думаю, что эта строк адолжна стоять первой
        self.global_time += 1
        self.season_time +=1
        if self.season_time == cn.MONTHS:
            self.season_time = 0

    def plant_setup_1(self):
        for _ in range(5):
            id = Field.coord_to_id(int(cn.FIELDS_NUMBER_BY_SIDE / 2), int(cn.FIELDS_NUMBER_BY_SIDE / 2))
            self.create_plant(id)

    def plant_setup_2(self):
        for x in range(int(cn.FIELDS_NUMBER_BY_SIDE / 2) - 2, int(cn.FIELDS_NUMBER_BY_SIDE / 2) + 3):
            for y in range(int(cn.FIELDS_NUMBER_BY_SIDE / 2) - 2, int(cn.FIELDS_NUMBER_BY_SIDE / 2) + 3):
                id = Field.coord_to_id(x, y)
                self.create_plant(id)

    def plant_setup_3(self):
        for x in range(cn.FIELDS_NUMBER_BY_SIDE):
            for y in range(cn.FIELDS_NUMBER_BY_SIDE):
                id = Field.coord_to_id(x, y)
                self.create_plant(id)


    def create_fields(self):
        for row in range(cn.FIELDS_NUMBER_BY_SIDE):
            for col in range(cn.FIELDS_NUMBER_BY_SIDE):
                f =  Field(self, row, col, cn.INIT_SOIL)
                self.fields[f.id] = f

    def create_plant(self, id):
        self.fields[id].create_plant()

    def create_seed(self, id, seed_mass):
        self.fields[id].create_seed(seed_mass)


    def update_fields(self):
        for f in self.fields.values():
            f.update()

    def update_objects(self):
        self.drop_changed_objects()
        for field in self.fields.values():
            for func in (Field.update_rot, Field.update_seeds, Field.update_plants):
                func(field)
            field.update_objs()
        self.gather_changed_objects()

    def drop_changed_objects(self):
        self.change_scene = {'new': [], 'obsolete': []}

    def gather_changed_objects(self):
        """
        Пробегаем по полю и собираем с каждой клетки словари ноавх и устаревших объектов
        """
        for field in self.fields.values():
            for key in ('new', 'obsolete'):
                changes = field.change_field_objects[key]
                if changes:
                    self.change_scene[key].extend(changes)
