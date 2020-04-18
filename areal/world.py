from tkinter import *
import random
import math

from areal import constants as cn
from areal import weather
from areal import field as fd

# для эксперимента у всех констант будут единичные значения, а потом эти константы будут загружаться из конфига
#random.seed(666)


plants_info = open('plants_info.csv', 'w', encoding='UTF16')
header = 'year\tglob time\ttotal plants\tfull\tstarving\tseeds\trot\tseed mass\tbiomass\trot mass\tsoil\ttotal mass\n'
plants_info.write(header)

class World:
    def __init__(self, parent):
        self.canvas = Canvas(parent, width=cn.WIDTH, heigh=cn.HEIGHT, bg='gray80')
        self.canvas.pack(expand=YES, fill=BOTH)
        # создаем пустое игровое поле
        temp = [None for _ in range(cn.FIELDS_NUMBER_BY_SIDE)]
        self.fields = [temp[:] for x in range(cn.FIELDS_NUMBER_BY_SIDE)]
        self.time = 0
        self.global_time = 0
        self.years = 0
        self.total_soil = 0
        self.seeds = {}
        self.plants = {}
        self.rot = {}
        self.to_breed = []
        self.weather = weather.Weather()
        self.create_fields()

        self.plant_setup_3()
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
                self.fields[row][col] = fd.Field(self, row, col)


    def create_plant(self, row, col):
        self.fields[row][col].create_plant()

    def create_seed(self, row, col, seed_mass):
        self.fields[row][col].create_seed(seed_mass)

    def update_seeds(self):
        seeds_list = list(self.seeds)
        for seed in seeds_list:
            self.seeds[seed].update()

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
        print(len(plant_list))
        for p in plant_list:
            self.plants[p].update()

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
        self.total_soil = 0
        for row in range(cn.FIELDS_NUMBER_BY_SIDE):
            for col in range(cn.FIELDS_NUMBER_BY_SIDE):
                '''
                вычисляется цвет температуры
                x, y = graph_to_phys(row, col)
                cur_temp =  self.weather.temp_in_field(x, y, self.time)
                back = self.calculate_color(cur_temp)
                '''
                #цвет почвы
                self.fields[row][col].info()
                self.total_soil += self.fields[row][col].soil
                back = self.soil_color(self.fields[row][col])
                self.fields[row][col].set_color(back)


    def write_plants(self):
        s = f'{self.years}\t{self.global_time}\t{len(self.plants)}\t'
        full = 0
        starving = 0
        biomass = 0
        for p in self.plants:
            self.plants[p].info()
            biomass += self.plants[p].all_consumed_food
            if self.plants[p].delta >= 0:
                full += 1
            else:
                starving +=1
        rot_mass = 0
        for r in self.rot:
            rot_mass += self.rot[r].mass
        seed_mass = 0
        for seed in self.seeds:
            seed_mass += self.seeds[seed].all_food
        s += f'{full}\t{starving}\t{len(self.seeds)}\t{len(self.rot)}\t'
        total_mass = seed_mass + biomass + rot_mass + self.total_soil
        s += f'{seed_mass:8.1f}\t{biomass:8.1f}\t{rot_mass:8.1f}\t{self.total_soil:8.1f}\t{total_mass:8.1f}\n'
        plants_info.write(s.replace('.', ','))




    def update(self):
        self.global_time += 1
        self.years = self.global_time//cn.MONTHS
        print(f'------ TIME: {self.years}:{self.time}')
        print(f'soil: {self.total_soil:8.2f}')
        self.time +=1
        if self.time == cn.MONTHS:
            self.time = 0
        self.update_rot()
        self.update_seeds()
        self.update_plants()
        self.update_fields()
        self.write_plants() # запись параметров всех растений в файлы
        if self.global_time < cn.MONTHS * cn.SIMULATION_PERIOD:
            self.canvas.after(80, self.update)

