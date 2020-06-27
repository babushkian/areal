import time
import os
from areal import constants as cn
from areal.world import World
from areal.graphics import GW
from areal.base import WorldBase
from areal.log import Log
from areal.plant import Plant
from areal.seed import Seed
from areal.rot import Rot

class Heaven:
    def __init__(self, app):
        self.app = app
        self.world = World()
        if cn.GRAPHICS:
            self.graph = GW()
        else:
            self.graph = None
        self.db = None
        self.sim_number = 0
        self.sim_dir  = self.init_sim_dir()
        self.game_over = False
        self.time_over = False
        self.perish = False
        self.starving = 0  # растения, не получющие необходимое количество пищи
        self.starving_percent = 0
        self.world_mass = 0
        self.seed_mass = 0
        self.plant_mass = 0
        self.rot_mass = 0
        self.soil_mass = 0 # полная масса системы: почва растения, семена и гниль
        self.sign_plant_num = 0
        self.sign_plant_mass_energy = 0
        self.sign_plant_mass_integral = 0
        self.sign_seeds_born = 0
        self.sign_seeds_grow_up = 0
        self.soil_flow = 0# МЕТРИКА: сколько гнили переработалось в почву за весь период симулчяции
        self.living_beings = 0

    @staticmethod
    def init_sim_dir():
        cur_date = time.time()
        sim_dir = 'sim_' + time.strftime("%d.%m.%Y_%H.%M.%S", time.localtime(cur_date))
        try:
            os.mkdir(sim_dir)
        except:
            raise Exception('Не удалось создать каталог симуляции')
        return sim_dir

    def init_sim(self):
        def param_tuple():
            t = [self.sim_number]
            t.append(cn.FIELDS_NUMBER_BY_SIDE)
            t.append(cn.SIMULATION_PERIOD)
            t.append(cn.MAX_PLANTS_IN_FIELD)
            t.append(cn.INIT_SOIL)
            t.append(cn.SEED_GROW_UP_CONDITION)
            t.append(cn.SEED_LIFE)
            t.append(cn.SEED_PROHIBITED_GROW_UP)
            t.append(cn.PLANT_LIFETIME_YEARS)
            t.append(cn.FRUITING_PERIOD)
            t.append(cn.PLANT_HIDDEN_MASS)
            t.append(cn.SEED_MASS)
            t.append(cn.PLANT_MAX_MASS)
            return tuple(t)

        self.db = WorldBase(self)
        self.db.insert_params(param_tuple())
        self.db.insert_time()
        metr = os.path.join(self.sim_dir, 'metric.csv')
        self.metric_file = open(metr, 'w', encoding='UTF16')
        self.logging = Log(self)
        self.logging.population_metric_head(self.metric_file)
        self.world.init_sim()
        for row in range(cn.FIELDS_NUMBER_BY_SIDE):
            for col in range(cn.FIELDS_NUMBER_BY_SIDE):
                self.db.insert_field(self.world.fields[row][col])
        self.db.db_write()


    def update(self):
        self.world.time_pass()
        self.db.insert_time()
        self.world.update()
        self.db.db_write()
        self.living_beings = Plant.COUNT + Seed.COUNT # проверяем, есть кто живой на карте

        self.statistics() # изменить двойной цикл по клеткам на одинарный
        self.logging.write()
        if self.world.global_time % (3*cn.MONTHS) == 0:
            self.db.commit()
        self.check_end_of_simulation()
        if not self.game_over:
            if cn.GRAPHICS and self.app.sim_state:
                self.graph.update_a()
        else:
            self.end_of_simulation()


    def check_end_of_simulation(self):
        if not self.world.global_time < cn.MONTHS * cn.SIMULATION_PERIOD:
            self.time_over = True
            self.game_over = True
        if self.count_of_world_objects < 1:
            self.perish = True
            self.game_over = True


    def end_of_simulation(self):
        if cn.GRAPHICS:
            self.graph.display_end_of_simulation()
        self.logging.population_metric_record(self.metric_file)
        self.metric_file.flush()
        self.db.close_connection()
        self.logging.logging_close()


    def statistics(self):
        self.soil_mass = 0
        self.seed_mass = 0
        self.plant_mass = 0
        self.rot_mass = 0
        self.starving = 0
        for row in range(cn.FIELDS_NUMBER_BY_SIDE):
            for col in range(cn.FIELDS_NUMBER_BY_SIDE):
                # считаем статистику
                # подсчет масс растений семян, гнили и почвы на каждой клетке
                field = self.world.fields[row][col]
                field.info()
                self.db.update_soil(field)
                # подсчет полной массы почвы на на игровом поле
                self.soil_mass += field.soil
                self.seed_mass += field.seed_mass
                self.plant_mass += field.plant_mass
                self.rot_mass += field.rot_mass
                self.starving += field.starving
        self.sign_plant_mass_integral += self.plant_mass
        if self.starving == 0:
            self.starving_percent = 0
        else:
            self.starving_percent = self.starving / Plant.COUNT * 100
        self.world_mass = self.soil_mass + self.seed_mass + self.plant_mass + self.rot_mass
        self.count_of_world_objects = Plant.COUNT + Seed.COUNT + Rot.COUNT
