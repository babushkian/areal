from tkinter import *
import random
import math



# для эксперимента у всех констант будут единичные значения, а потом эти константы будут загружаться из конфига

random.seed(666)
MONTS = 1  # кличество тиков в одном году. позволяет настраивать плавность развития
MAX_WIDNDOW = 1 # максимальная высота игрового поля в пикселях
DIMENSION = 1  # прространственная размерность: +- 100 по обоим координатам
CHECK_DIM = 1  # размер одной клетки в пикселях
DRAW_DIM = 1  # размерность поля в клетках


WIDTH = 1
HEIGHT = 1
DIM_HYPOT = 1
MONTS_ANGLE = 1

from areal import weather
from areal import field as fd

def init_constants():
    global WIDTH
    global HEIGHT
    global DIM_HYPOT
    global MONTS_ANGLE
    global CHECK_DIM

    if CHECK_DIM * DRAW_DIM > MAX_WIDNDOW:
        CHECK_DIM = MAX_WIDNDOW // DRAW_DIM
    WIDTH = CHECK_DIM * DRAW_DIM # размеры окна в пикселях
    HEIGHT = CHECK_DIM * DRAW_DIM
    DIM_HYPOT = math.hypot(DIMENSION, DIMENSION)
    MONTS_ANGLE = math.pi * 2 / MONTS  # погодный угол, за год проходит все 360 градусов
    print('Значения переменных загружены')

    print("CHECK_DIM ", CHECK_DIM)
    print("DRAW_DIM ", DRAW_DIM)
    print("DIM_HYPOT ", DIM_HYPOT)
    print("MONTS ", MONTS)
    print("DIMENSION ", DIMENSION)
    print("WIDTH  ", WIDTH )
    fd.Field.init_constants()



plants_info = open('plants_info.csv', 'w', encoding='UTF16')
header = 'year\tglob time\ttotal plants\tfull\tstarving\tseeds\trot\tseed mass\tbiomass\trot mass\tsoil\ttotal mass\n'
plants_info.write(header)

class World:
    def __init__(self, parent):
        self.canvas = Canvas(parent, width=WIDTH, heigh=HEIGHT, bg='gray80')
        self.canvas.pack(expand=YES, fill=BOTH)
        # создаем пустое игровое поле
        temp = [None for _ in range(DRAW_DIM)]
        self.fields = [temp[:] for x in range(DRAW_DIM)]
        self.time = 0
        self.global_time = 0
        self.years = 0
        self.total_soil = 0
        self.seeds = {}
        self.plants = {}
        self.rot = {}
        self.to_breed = []
        self.wead = weather.Weather()
        self.create_fields()

        #for v in range(int(DRAW_DIM/2)-1, int(DRAW_DIM/2)+2):
        #    self.fields[int(DRAW_DIM/2)][v].soil = 7000

        self.plant_setup_3()
        self.update()

    def calculate_color(self, temp):
        t = (temp + 14)* 1.6
        color = 'gray%d' % t
        return color

    def plant_setup_1(self):
        for _ in range(5):
            self.create_plant(int(DRAW_DIM/2), int(DRAW_DIM/2))

    def plant_setup_2(self):
        for x in range(int(DRAW_DIM/2)-2, int(DRAW_DIM/2)+3):
            for y in range(int(DRAW_DIM / 2) - 2, int(DRAW_DIM / 2) + 3):
                self.create_plant(x, y)

    def plant_setup_3(self):
        for x in range(DRAW_DIM):
            for y in range(DRAW_DIM):
                self.create_plant(x, y)


    def create_fields(self):
        for row in range(DRAW_DIM):
            for col in range(DRAW_DIM):
                self.fields[row][col] = fd.Field(self, row, col)


    def create_plant(self, row, col):
        self.fields[row][col].create_plant()

    def create_seed(self, row, col):
        self.fields[row][col].create_seed()

    def update_seeds(self):
        seeds_list = list(self.seeds)
        for seed in seeds_list:
            self.seeds[seed].update()

    def breed_plants(self):
        for p in self.to_breed:
            # выбираем случайную клетку в окрестностях, чтобы засеять семя
            l = len(p.field.area)
            field_coord = p.field.area[random.randrange(l)]
            self.create_seed(field_coord[0], field_coord[1])
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
        for row in range(DRAW_DIM):
            for col in range(DRAW_DIM):
                '''
                вычисляется цвет температуры
                x, y = graph_to_phys(row, col)
                cur_temp =  self.wead.temp_in_field(x, y, self.time)
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
        total_mass = biomass + rot_mass + self.total_soil
        s += f'{seed_mass:8.1f}\t{biomass:8.1f}\t{rot_mass:8.1f}\t{self.total_soil:8.1f}\t{total_mass:8.1f}\n'
        plants_info.write(s.replace('.', ','))




    def update(self):
        self.global_time += 1
        self.years = self.global_time//MONTS
        print('------ TIME: %d:%02d' % (self.years, self.time))
        print('soil: %8.2f' % self.total_soil)
        self.time +=1
        if self.time == MONTS:
            self.time = 0
        self.update_rot()
        self.update_seeds()
        self.update_plants()
        self.update_fields()
        self.write_plants() # запись параметров всех растений в файлы
        if self.global_time < MONTS * 10000:
            self.canvas.after(80, self.update)

