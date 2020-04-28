from tkinter import *
import math

from areal import constants as cn
from areal import weather


plants_info = open('plants_info.csv', 'w', encoding='UTF16')
header = 'year\tglob time\ttotal plants\tfull\tstarving\tseeds\trot\tseed mass\tbiomass\trot mass\tsoil\ttotal mass\n'

plants_info.write(header)
from areal.field import Field
from areal.plant import Plant
from areal.seed import Seed
from areal.rot import Rot


class World(Canvas):
    def __init__(self, parent, app):
        super().__init__(parent, width=cn.WIDTH, heigh=cn.HEIGHT, bg='gray50')
        self.app = app

        self.newborn = True
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


    def run(self):
        if self.newborn:
            self.create_fields()
            self.plant_setup_3()
            self.newborn = False
            self.delay = cn.define_delay()
        self.update()

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
                #цвет клетки
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

    def write_plants(self):
        s = f'{self.years}\t{self.global_time}\t{Plant.COUNT}\t'
        s += f'{Plant.COUNT - self.starving}\t{self.starving}\t'
        s += f'{Seed.COUNT}\t'
        s += f'{Rot.COUNT}\t'
        s += f'{self.seed_mass:8.1f}\t{self.plant_mass:8.1f}\t{self.rot_mass:8.1f}\t'
        s += f'{self.soil_mass:8.1f}\t{self.world_mass:8.1f}\n'
        plants_info.write(s.replace('.', ','))


    def update(self):
        self.years = self.global_time // cn.MONTHS
        self.global_time += 1
        self.season_time +=1
        if self.season_time == cn.MONTHS:
            self.season_time = 0
        self.update_rot()
        self.update_seeds()
        self.update_plants()
        self.tag_raise('plant')
        if cn.GRAPH_FIELD:
            self.update_fields()
        self.statistics() # изменить двойной цикл по клеткам на одинарный
        self.write_plants() # запись параметров всех растений в файлы
        if self.app.sim_state and self.global_time < cn.MONTHS * cn.SIMULATION_PERIOD:
            self.after(self.delay, self.update)

