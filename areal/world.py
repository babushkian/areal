from tkinter import *
import random
import math

from areal import constants as cn
from areal import weather
from areal import field as fd


plants_info = open('plants_info.csv', 'w', encoding='UTF16')
header = 'year\tglob time\ttotal plants\tfull\tstarving\tseeds\trot\tseed mass\tbiomass\trot mass\tsoil\ttotal mass\n'
plants_info.write(header)

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

        self.plant_num = 0
        self.seed_num = 0
        self.rot_num = 0
        self.starving = 0  # растения, не получющие необходимое количество пищи
        self.starving_percent = 0
        self.world_mass = 0
        self.seed_mass = 0
        self.plant_mass = 0
        self.rot_mass = 0
        self.soil_mass = 0 # полная масса системы: почва растения, семена и гниль

        self.seeds = {}
        self.plants = {}
        self.rot = {}

        self.to_breed = []
        self.weather = weather.Weather()
        self.create_fields()


    def run(self):
        if self.newborn:
            self.plant_setup_3()
            self.newborn = False
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
                self.fields[row][col] = fd.Field(self, self.app, row, col)

    def create_plant(self, row, col):
        self.fields[row][col].create_plant()

    def create_seed(self, row, col, seed_mass):
        self.fields[row][col].create_seed(seed_mass)

    def breed_plants(self):
        for p in self.to_breed:
            # выбираем случайную клетку в окрестностях, чтобы засеять семя
            l = len(p.field.area)
            field_coord = p.field.area[random.randrange(l)]
            seed_mass = p.split_mass()
            self.create_seed(field_coord[0], field_coord[1], seed_mass)
        self.to_breed = []

    def update_plants(self):
        if self.to_breed:
            self.breed_plants()
        plant_list = list(self.plants)
        # перемешивание растений и семян для более равномерного готбора
        pl = len(plant_list)
        if pl > 3:
            for _ in range(cn.FIELDS_NUMBER_BY_SIDE): # неаонятно, есть ли эффект от перемешивания? Не заметно
                pl = len(plant_list)
                x = random.randrange(pl)
                y = random.randrange(pl)
            plant_list[x], plant_list[y] = plant_list[y], plant_list[x]
        for p in plant_list:
            self.plants[p].update()

    def update_seeds(self):
        seeds_list = list(self.seeds)
        pl = len(seeds_list)
        if pl > 3:
            for _ in range(cn.FIELDS_NUMBER_BY_SIDE): # неаонятно, есть ли эффект от перемешивания? Не заметно
                x = random.randrange(pl)
                y = random.randrange(pl)
            seeds_list[x], seeds_list[y] = seeds_list[y], seeds_list[x]
        for seed in seeds_list:
            self.seeds[seed].update()

    def update_rot(self):
        rot_list = list(self.rot)
        for r in rot_list:
            #self.rot[r].update()
            self.rot[r].update_continuous()


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
        self.plant_num = 0
        self.seed_num = 0
        self.rot_num = 0
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
                self.plant_num += field.plant_num
                self.seed_num += field.seed_num
                self.rot_num += field.rot_num
                self.starving += field.starving
        if self.starving == 0:
            self.starving_percent = 0
        else:
            self.starving_percent = self.starving / self.plant_num * 100
        self.world_mass = self.soil_mass + self.seed_mass + self.plant_mass + self.rot_mass

    header = 'year\tglob time\ttotal plants\tfull\tstarving\tseeds\trot\tseed mass\tbiomass\trot mass\tsoil\ttotal mass\n'
    def write_plants(self):
        s = f'{self.years}\t{self.global_time}\t{self.plant_num}\t'
        s += f'{self.plant_num - self.starving}\t{self.starving}\t{self.seed_num}\t{self.rot_num}\t'
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
            self.after(cn.AFTER_COOLDOWN, self.update)

