import time
import os
from areal import constants as cn
from areal.world import World
from areal.graphics import GW
from areal.base import WorldBase
from areal.log import Log, population_metric_head
from areal.plant import Plant
from areal.seed import Seed
from areal.rot import Rot

SIM_DIR = None
METRIC_FILE = None

class Heaven:
    SIM_NUMBER = 0
    def __init__(self, app):
        self.app = app
        self.world = World()
        if cn.GRAPHICS:
            self.graph = GW()
        else:
            self.graph = None
        self.db = None
        Heaven.SIM_NUMBER += 1
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


    def init_sim(self):
        def param_tuple():
            t = [self.SIM_NUMBER]
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

        self.db = WorldBase(self, SIM_DIR)
        self.db.insert_params(param_tuple())
        self.db.insert_time()
        self.logging = Log(self, SIM_DIR)
        self.world.init_sim()
        for field in self.world.fields.values():
            self.db.insert_field(field)
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
        self.logging.population_metric_record(METRIC_FILE)
        METRIC_FILE.flush()
        self.db.close_connection()
        self.logging.logging_close()


    def statistics(self):
        self.soil_mass = 0
        self.seed_mass = 0
        self.plant_mass = 0
        self.rot_mass = 0
        self.starving = 0
        for field in self.world.fields.values():
            # считаем статистику
            # подсчет масс растений семян, гнили и почвы на каждой клетке
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


def init_sim_dir():
    global SIM_DIR
    cur_date = time.time()
    SIM_DIR = 'sim_' + time.strftime("%d.%m.%Y_%H.%M.%S", time.localtime(cur_date))
    try:
        os.mkdir(SIM_DIR)
    except:
        raise Exception('Не удалось создать каталог симуляции')
    return SIM_DIR

def init_metric():
    global METRIC_FILE
    metr = os.path.join(SIM_DIR, 'metric.csv')
    METRIC_FILE = open(metr, 'w', encoding='UTF16')
    population_metric_head(METRIC_FILE)
