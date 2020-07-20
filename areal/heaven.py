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
    def __init__(self, frame, app):
        self.app = app
        self.frame = frame
        self.world = World()
        if cn.GRAPHICS:
            self.graph = GW(self)
        else:
            self.graph = None
        self.db = None
        Heaven.SIM_NUMBER += 1
        self.calculated = False # признак, что новое состояние посчиталось и его можно выводить на экран
        self.game_over = False
        self.simulation_closed = False # выполнены действия по достижении конца симуляции. Чтобы второй раз не вызывалось
        self.time_over = False
        self.perish = False
        self.starving = 0  # растения, не получющие необходимое количество пищи
        self.starving_percent = 0
        self.world_mass = 0
        self.seed_mass = 0
        self.plant_mass = 0
        self.rot_mass = 0
        self.soil_mass = 0 # полная масса системы: почва растения, семена и гниль
        # метрики
        self.sign_plant_num = 0 # кличество растений, рожденных за время симуляции
        self.sign_seeds_born = 0 # количество семян за время симуляции
        self.sign_rot_amount = 0 # коичество гнили за время симуляции, показывает оборот биомассы
        self.sign_seeds_grow_up = 0 # количество семян, проросших за время симуляции
        self.sign_plant_mass_energy = 0
        self.sign_plant_mass_integral = 0
        self.soil_flow = 0# МЕТРИКА: сколько гнили переработалось в почву за весь период симулчяции
        self.living_beings = 0


    def init_sim(self):
        self.db = WorldBase(self, SIM_DIR)
        self.db.insert_params()
        #self.db.insert_time()
        self.logging = Log(self, SIM_DIR)
        self.world.init_sim()
        if cn.GRAPHICS:
            self.graph.init_sim()

        for field in self.world.fields.values():
            self.db.insert_field(field)
        self.db.db_write()


    def update(self):
        if not self.calculated or not cn.GRAPHICS: # срабатывает, если calculated = False (рассчитанный кадр был отображен в graphics)
            self.world.time_pass()
            self.world.update()

            self.db.db_write()
            self.living_beings = Plant.COUNT + Seed.COUNT # проверяем, есть кто живой на карте

            self.statistics()
            self.logging.write()
            if self.world.global_time % (3*cn.MONTHS) == 0:
                self.db.commit()
            self.calculated = True
            self.check_end_of_simulation()
            if self.game_over:
                self.end_of_simulation()

    def check_end_of_simulation(self):
        if not self.world.global_time < cn.MONTHS * cn.SIMULATION_PERIOD:
            self.time_over = True
            self.game_over = True
        if self.count_of_world_objects < 1:
            self.perish = True
            self.game_over = True


    def end_of_simulation(self):
        # это остановка симуляции, все объекты остаются нетронутыми
        # закрываются файлы и связь с базой
        if not self.simulation_closed:
            if cn.GRAPHICS:
                self.graph.display_end_of_simulation()
            self.logging.population_metric_record(METRIC_FILE)
            METRIC_FILE.flush()
            metric = (self.sign_plant_num, self.sign_seeds_born, self.sign_rot_amount,
                      self.sign_seeds_grow_up, self.sign_plant_mass_integral, self.soil_flow)
            self.db.insert_metric(metric)
            self.db.close_connection()
            self.logging.logging_close()
            self.simulation_closed = True


    def delete_simulation(self):
    # удаление симуляции. удаляются все внутрнние объекты, включая графическое представление
        del self.world
        del self.logging
        del self.db
        if cn.GRAPHICS:
            self.graph.destroy()

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
        self.soil_flow += self.soil_mass
        if self.starving == 0:
            self.starving_percent = 0
        else:
            self.starving_percent = self.starving / Plant.COUNT * 100
        # вычисление метрик
        born_plants = 0 # рожденные на этом ходу растения (для вычисления проросших семян)
        for o in self.world.change_scene['new'].values():
            if o.name == 'plant':
                self.sign_plant_num += 1
                born_plants += 1
            if o.name == 'seed':
                self.sign_seeds_born += 1
            if o.name == 'rot':
                self.sign_rot_amount += o.all_energy
        # сколько растений проросло за ход. Часть семян превращается в растения, а часть в гниль.
        # Смотрим, скольо семян устарело, а сколько растений появилось
        obsolete_seeds = 0
        for o in self.world.change_scene['obsolete'].values():
            if o.name == 'seed':
                obsolete_seeds += 1
        self.sign_seeds_grow_up += min(born_plants, obsolete_seeds)

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
