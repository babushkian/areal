from areal import constants as cn
from areal import weather
from areal.field import Field
from areal.plant import Plant
from areal.seed import Seed
from areal.rot import Rot

class World():
    def __init__(self):
        # создаем пустое игровое поле
        temp = [None for _ in range(cn.FIELDS_NUMBER_BY_SIDE)]
        self.fields = [temp[:] for x in range(cn.FIELDS_NUMBER_BY_SIDE)]
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
            self.create_plant(int(cn.FIELDS_NUMBER_BY_SIDE / 2), int(cn.FIELDS_NUMBER_BY_SIDE / 2))

    def plant_setup_2(self):
        for x in range(int(cn.FIELDS_NUMBER_BY_SIDE / 2) - 2, int(cn.FIELDS_NUMBER_BY_SIDE / 2) + 3):
            for y in range(int(cn.FIELDS_NUMBER_BY_SIDE / 2) - 2, int(cn.FIELDS_NUMBER_BY_SIDE / 2) + 3):
                self.create_plant(x, y)

    def plant_setup_3(self):
        for x in range(cn.FIELDS_NUMBER_BY_SIDE):
            for y in range(cn.FIELDS_NUMBER_BY_SIDE):
                self.create_plant(x, y)


    def create_fields(self):
        for row in range(cn.FIELDS_NUMBER_BY_SIDE):
            for col in range(cn.FIELDS_NUMBER_BY_SIDE):
                self.fields[row][col] =  Field(self, row, col, cn.INIT_SOIL)


    def create_plant(self, row, col):
        self.fields[row][col].create_plant()

    def create_seed(self, row, col, seed_mass):
        self.fields[row][col].create_seed(seed_mass)


    def update_fields(self):
        for row in range(cn.FIELDS_NUMBER_BY_SIDE):
            for col in range(cn.FIELDS_NUMBER_BY_SIDE):
                self.fields[row][col].update()

    def update_objects(self):
        self.drop_changed_objects()
        for func in (Field.update_rot, Field.update_seeds, Field.update_plants):
            for row in range(cn.FIELDS_NUMBER_BY_SIDE):
                for col in range(cn.FIELDS_NUMBER_BY_SIDE):
                    func(self.fields[row][col])
                    self.fields[row][col].update_objs()
                    #print(self.fields[row][col].objects)
        self.gather_changed_objects()

    def drop_changed_objects(self):
        self.change_scene = {'new': [], 'obsolete': []}

    def gather_changed_objects(self):
        """
        Пробегаем по полю и собираем с каждой клетки словари ноавх и устаревших объектов
        """
        for row in range(cn.FIELDS_NUMBER_BY_SIDE):
            for col in range(cn.FIELDS_NUMBER_BY_SIDE):
                for key in ('new', 'obsolete'):
                    changes = self.fields[row][col].change_field_objects[key]
                    if changes:
                        self.change_scene[key].extend(changes)
