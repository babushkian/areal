from tkinter import *
from tkinter import font
import math
import random

from areal import constants as cn
from areal import weather

from areal.field import Field
from areal.plant import Plant
from areal.seed import Seed
from areal.rot import Rot


class World(Canvas):
    def __init__(self, parent, app):
        super().__init__(parent, width=cn.WIDTH, heigh=cn.HEIGHT, bg='gray50')
        self.pack()
        self.app = app

        self.newborn = True # смиуляция только создана и еще не запускалась
        self.game_ower  = False # симуляция закончена по той или иной причине
        self.time_ower = False # истек срок симуляции
        self.perish = False # все вымерли
        self.show_end = False # выводилась ли надпись об окончании игры
        # создаем пустое игровое поле
        temp = [None for _ in range(cn.FIELDS_NUMBER_BY_SIDE)]
        self.fields = [temp[:] for x in range(cn.FIELDS_NUMBER_BY_SIDE)]
        self.season_time = 0
        self.global_time = 0
        self.years = 0
        self.starving = 0  # растения, не получющие необходимое количество пищи
        self.starving_percent = 0
        self.world_mass = 0
        self.seed_mass = 0
        self.plant_mass = 0
        self.rot_mass = 0
        self.soil_mass = 0 # полная масса системы: почва растения, семена и гниль

        self.weather = weather.Weather()
        self.logfile_associations = {'every_plant_life': self.log_plants,
                             'fields_info': self.log_fields,
                             'world_info': self.log_world}
        self.log_functions = {} # словарь содержит функции, которые должны вызываться для логирования ключевого файла
        self.logging_prepare()

    def run(self):
        if self.newborn:
            self.create_fields()
            self.plant_setup_3()
            self.newborn = False
            self.delay = cn.define_delay()
        if not self.game_ower:
            self.update_a()

    def calculate_color(self, temp):
        t = (temp + 14)* 1.6
        color = 'gray%d' % t
        return color

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
                self.fields[row][col] = Field(self, row, col)

    def create_plant(self, row, col):
        self.fields[row][col].create_plant()

    def create_seed(self, row, col, seed_mass):
        self.fields[row][col].create_seed(seed_mass)


    def update_plants(self):
        for row in range(cn.FIELDS_NUMBER_BY_SIDE):
            for col in range(cn.FIELDS_NUMBER_BY_SIDE):
                self.fields[row][col].update_plants()


    def update_seeds(self):
        for row in range(cn.FIELDS_NUMBER_BY_SIDE):
            for col in range(cn.FIELDS_NUMBER_BY_SIDE):
                self.fields[row][col].update_seeds()

    def update_rot(self):
        for row in range(cn.FIELDS_NUMBER_BY_SIDE):
            for col in range(cn.FIELDS_NUMBER_BY_SIDE):
                self.fields[row][col].update_rot()


    def soil_color(self, field):
        t = int(7*math.log2(field.soil+1))
        color = 'gray%d' % t
        return color


    def update_fields(self):
        for row in range(cn.FIELDS_NUMBER_BY_SIDE):
            for col in range(cn.FIELDS_NUMBER_BY_SIDE):
                self.fields[row][col].update()
                #цвет клетки
                if cn.GRAPH_FIELD:
                    back = self.soil_color(self.fields[row][col])
                    self.fields[row][col].set_color(back)

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
                field = self.fields[row][col]
                field.info()
                # подсчет полной массы почвы на на игровом поле
                self.soil_mass += field.soil
                self.seed_mass += field.seed_mass
                self.plant_mass += field.plant_mass
                self.rot_mass += field.rot_mass
                self.starving += field.starving
        if self.starving == 0:
            self.starving_percent = 0
        else:
            self.starving_percent = self.starving / Plant.COUNT * 100
        self.world_mass = self.soil_mass + self.seed_mass + self.plant_mass + self.rot_mass

    header = 'year\tglob time\ttotal plants\tfull\tstarving\tseeds\trot\tseed mass\tbiomass\trot mass\tsoil\ttotal mass\n'

    def update_a(self):
        self.update_fields()
        self.years = self.global_time // cn.MONTHS
        self.global_time += 1
        self.season_time +=1
        if self.season_time == cn.MONTHS:
            self.season_time = 0
        self.update_rot()
        self.update_seeds()
        self.update_plants()
        self.tag_raise('plant')
        self.statistics() # изменить двойной цикл по клеткам на одинарный
        self.write_logs()
        self.check_end_of_simulation()
        if not self.game_ower:
            if self.app.sim_state:
                self.after(self.delay, self.update_a)
        else:
            self.end_of_simulation()

    def check_end_of_simulation(self):
        if not self.global_time < cn.MONTHS * cn.SIMULATION_PERIOD:
            self.time_ower = True
            self.game_ower = True
        if Plant.COUNT + Seed.COUNT + Rot.COUNT < 1:
            self.perish = True
            self.game_ower = True

    def end_of_simulation(self):
        self.show_end = True
        if cn.GRAPHICS:
            bigfont = font.Font(family='arial', size=20, weight="bold")
            if self.time_ower:
                self.create_text(360, 360, text='НАСТУПИЛА ПРЕДЕЛЬНАЯ ДАТА СИМУЛЯЦИИ', font=bigfont, fill='blue')
            if self.perish:
                self.create_text(360, 400, text='ПОПУЛЯЦИЯ ВЫМЕРЛА', font=bigfont, fill='blue')
        self.logging_close()

    def log_world(self, file):
        s = f'{self.years}\t{self.global_time}\t{Plant.COUNT}\t'
        s += f'{Plant.COUNT - self.starving}\t{self.starving}\t'
        s += f'{Seed.COUNT}\t'
        s += f'{Rot.COUNT}\t'
        s += f'{self.seed_mass:8.1f}\t{self.plant_mass:8.1f}\t{self.rot_mass:8.1f}\t'
        s += f'{self.soil_mass:8.1f}\t{self.world_mass:8.1f}\n'
        file.write(s.replace('.', ','))

    def log_fields(self, file):
        for row in range(cn.FIELDS_NUMBER_BY_SIDE):
            for col in range(cn.FIELDS_NUMBER_BY_SIDE):
                file.write(self.fields[row][col].write_info())


    def log_plants(self, file):
        for row in range(cn.FIELDS_NUMBER_BY_SIDE):
            for col in range(cn.FIELDS_NUMBER_BY_SIDE):
                for plant in self.fields[row][col].plants.values():
                    file.write(plant.info())


    def file_suffix(self):
        suffix = ['']
        suffix.append(f'sgc{cn.SEED_GROW_UP_CONDITION}')
        suffix.append(f'sl{cn.SEED_LIFE}')
        suffix.append(f'spg{cn.SEED_PROHIBITED_GROW_UP}')
        suffix.append(f'pl{cn.PLANT_LIFETIME_YEARS}')
        suffix.append(f'sm{cn.SEED_MASS}')
        suffix.append(f'pm{cn.PLANT_MAX_MASS}')
        suffix.append(f'{random.randint(1, 100000):06d}')
        s = '_'.join(suffix)
        return s
    def logging_prepare(self):
        suffix = self.file_suffix()
        for action, name, header  in cn.LOGGING:
            if action:
                f = open(f'{name}{suffix}.csv', 'w', encoding='UTF16')
                f.write(header)
                self.log_functions[f] = self.logfile_associations[name]

    def write_logs(self):
        for file in self.log_functions:
            self.log_functions[file](file)

    def logging_close(self):
        for file in self.log_functions:
            if not file.closed:
                file.close()
