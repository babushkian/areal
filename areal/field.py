import random
from collections import Counter


from areal import constants as cn
from areal.proto import Plant_proto
from areal.plant import Plant
from areal.seed import Seed


class Field:  # клетка поля
    # максимальное количество растений на клетку, чтобы симуляция не тормозила
    MAX_PLANTS_IN_FIELD = cn.MAX_PLANTS_IN_FIELD
    # физическое расстояние от центра до края клетки  (половина клетки!!, т.к. PHYS_SIZE - половина игрового поля)
    FIELD_GRAPH_TO_PHYS_PROPORTION = cn.PHYS_SIZE / cn.FIELDS_NUMBER_BY_SIDE

    def __init__(self, world, row, col, soil):
        self.world = world
        self.row = row
        self.col = col
        self.id = Field.coord_to_id(row, col)
        self.name = 'field'
        self.insert_soil(soil)
        self.tooltip = None
        self.starving = 0
        self.counts = Counter({'plant': 0, 'seed': 0})
        self.plants = dict() # словарь растений, размещенных на данной клетке; в качестве ключа - id графического объекта
        self.to_breed = list() # растения, готовые к размножению
        self.seeds = dict() # семена на клетке
        self.objects = list() # излишняя, нужно удалить, используется для записи объектов на клетек в базу
        self.seed_mass =0
        self.plant_mass = 0
        self.rot_mass = 0
        self.plant_ration = 0 # сколько можно скормить каждому растению за ход
        self.change_field_objects = {'new': dict(), 'obsolete': dict()}
        # физические координаты поля: его центра и краев
        self.center_x, self.center_y = Plant_proto.graph_to_phys(row, col)
        self.lu_x = self.center_x - self.FIELD_GRAPH_TO_PHYS_PROPORTION # left-up conner
        self.lu_y = self.center_y + self.FIELD_GRAPH_TO_PHYS_PROPORTION
        self.rd_x = self.center_x + self.FIELD_GRAPH_TO_PHYS_PROPORTION # right-down corner
        self.rd_y = self.center_y - self.FIELD_GRAPH_TO_PHYS_PROPORTION
        self.area = self.spread_area()  # соседние клетки, на которые происходит  распространиение семян
        self.num_of_neighbours = len(self.area)

    def spread_area(self):
        '''
        Возвращает соседей данной клетки, чтобы в них можно было посеять семена
        '''
        area = []
        borders = range(cn.FIELDS_NUMBER_BY_SIDE)
        r_start = self.row - 1
        c_start = self.col - 1
        for r in range(r_start, self.row +2):
            for c in range(c_start, self.col +2):
                self_field = r == self.row and c==self.col
                in_borders = r in borders and c in borders
                if not self_field and in_borders:  # проверяем, чтобы соседи не вылезали за границы игрового поля
                    area.append((r, c))
        return area


    def create_plant(self):
        """
        Вызывается из класса World при размножении расений
        Служит для инициалищзации растений  в начале симуляции. В дальнейшем не используется,
        так как растения прорастают из семян
        """
        # определяем координаты новорожденного растения
        # физические координаты
        x = self.lu_x + random.randrange(int(self.rd_x - self.lu_x))
        y = self.rd_y + random.randrange(int(self.lu_y - self.rd_y))
        if self.counts['plant'] < self.MAX_PLANTS_IN_FIELD:
            Plant(self, x, y)
        else:
            self.rot_mass += cn.TOTAL_SEED_MASS

    def create_seed(self, seed_mass):
        # определяем координаты новорожденного растения
        # физические координаты
        x = self.lu_x + random.randrange(int(self.rd_x - self.lu_x))
        y = self.rd_y + random.randrange(int(self.lu_y - self.rd_y))
        # экранные координаты
        Seed(self, x, y, seed_mass)

    def update(self):
        self.change_field_objects = {'new': dict(), 'obsolete': dict()}
        self.objects = list()  # излишняя, нужно удалить,

    def update_rot(self):
        new_soil = self.rot_mass if self.rot_mass < 1 else self.rot_mass / cn.DECAY_HALFLIFE
        self.rot_mass -= new_soil
        self.soil += new_soil

    def update_seeds(self):
        seeds_list = list(self.seeds)
        sl = len(seeds_list)
        if sl > 2: # перемешиваем семена, чтобы прорастали случайные, а не первые в списке
            x = random.randrange(sl)
            y = random.randrange(sl)
            seeds_list[x], seeds_list[y] = seeds_list[y], seeds_list[x]
        for seed in seeds_list:
            self.seeds[seed].update()

    def update_plants(self):
        if self.counts['plant'] > 0:
            if self.to_breed:
                self.breed_plants()
            plants_list = list(self.plants)
            self.plant_ration = self.soil/self.counts['plant']
            for plant in plants_list:
                self.plants[plant].update()

    def update_objs(self):
        for i in (self.plants, self.seeds):
            self.objects.extend(i.values())

    def breed_plants(self):
        for p in self.to_breed:
            # выбираем случайную клетку в окрестностях, чтобы засеять семя
            x, y = self.get_field_to_plant()
            id = self.coord_to_id(x, y)
            seed_mass = p.split_mass()
            self.world.create_seed(id, seed_mass)  # создается через world, так как смемена подают на соседние полянки
        self.to_breed = []

    def get_field_to_plant(self):
        if random.random() > cn.MIGRATION_PROB:
            return self.row, self.col
        else:
            return self.area[random.randrange(self.num_of_neighbours)]

    def add_to_new_pool(self, obj):
        self.change_field_objects['new'][obj.id] = obj

    def add_to_obsolete_pool(self, obj):
        self.change_field_objects['obsolete'][obj.id] = obj

    def info(self):
        self.starving = 0
        self.plant_mass = 0
        for p in self.plants:
            self.plant_mass += self.plants[p].all_energy
            if self.plants[p].delta < 0:
                self.starving += 1
        self.seed_mass = 0
        for s in self.seeds:
            self.seed_mass += self.seeds[s].all_energy

    def info_dict(self):
        s = dict()
        s['global time'] = f'{self.world.global_time}'
        s['coordinates'] = f'[{self.row:2d}][{self.col:2d}]'
        s['plants'] = f'{self.counts["plant"]:2d}'
        s['seeds'] = f'{self.counts["seed"]:2d}'
        s['biomass'] = f'{self.plant_mass:6.1f}'.replace('.', ',')
        s['rot mass'] = f'{self.rot_mass:6.1f}'.replace('.', ',')
        s['seeds mass'] = f'{self.seed_mass:6.1f}'.replace('.', ',')
        s['soil'] = f'{self.soil:6.1f}'.replace('.', ',')
        s['total mass'] = f'{(self.plant_mass + self.rot_mass + self.seed_mass + self.soil):7.1f}'.replace('.', ',')
        return s


    def insert_soil(self, soil):
        self.soil = soil

    @staticmethod
    def coord_to_id(row, col):
        return f'{row:02d}x{col:02d}'

    @staticmethod
    def id_to_coord(id):
        coord = id.split('x')
        row = int(coord[0])
        col = int(coord[1])
        return row, col