from math import ceil, floor, hypot
from random import random

from areal import constants as cn
from areal.field import Field
from areal.world import World

class WCreate:
    def __init__(self):
        self.world = World()

    def return_new_world(self):
        self.init_world()
        return self.world

    def init_world(self):
        self.world.init_sim()
        #self.field_fill_box(cn.FIELDS_NUMBER_BY_SIDE, 0)
        #self.field_fill_circle(5, 2200, offset_y= .25, grad= True)
        #self.field_fill_circle(5, 2200, offset_y= .75, grad=True)
        self.field_fill_circle(cn.FIELDS_NUMBER_BY_SIDE-2, 2200,  grad=True)
        #self.field_fill_box(5, 2200, grad=True, noise=True, noise_ampl=.1)
        #self.field_fill_box(3, 600, offset_y= 0.25)
        #self.field_fill_box(3, 5000, offset_y=0.75)
        self.world.plant_setup_3()
        self.world.gather_changed_objects()


    def field_fill_box(self, size, amount, offset_x=0.5, offset_y=0.5, grad=False, noise = False, noise_ampl=0.3):
        if size<1:
            return
        size = min(size, cn.FIELDS_NUMBER_BY_SIDE)
        centr_x = floor(cn.FIELDS_NUMBER_BY_SIDE * offset_x)
        centr_y = floor(cn.FIELDS_NUMBER_BY_SIDE * offset_y)
        halfsize = floor(size/2)
        start_x = centr_x - halfsize
        start_y = centr_y - halfsize
        end_x = centr_x + (size - halfsize)
        end_y = centr_y + (size - halfsize)

        start_x = 0 if start_x <0 else start_x
        start_y = 0 if start_y < 0 else start_y
        end_x = cn.FIELDS_NUMBER_BY_SIDE if end_x > cn.FIELDS_NUMBER_BY_SIDE else end_x
        end_y = cn.FIELDS_NUMBER_BY_SIDE if end_y > cn.FIELDS_NUMBER_BY_SIDE else end_y

        shoulder = ceil(size / 2)
        delta = abs(amount - cn.INIT_SOIL) / shoulder if shoulder > 0 else 0

        print('=======================')
        print(f'размер: {size}, halfsize: {halfsize}')
        print(f'центр {centr_x},{centr_y}')
        print(f'верхний левый {start_x}, {start_y}')
        print(f'нижний правый {end_x}, {end_y}')
        print(f'плечо {shoulder}  дельта {halfsize}')
        positions = [[None for _ in range(start_x, end_x)] for _ in range(start_y, end_y)]

        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                id = Field.coord_to_id(x, y)
                local_soil_amount = amount
                if grad:
                    reduse = max(abs(x - centr_x), abs(y - centr_y))
                    local_soil_amount = amount - delta * reduse

                if noise:
                    local_soil_amount =  local_soil_amount * (.5 + (random() - .5)*noise_ampl)

                local_soil_amount = cn.MAX_SOIL_ON_FIELD if local_soil_amount > cn.MAX_SOIL_ON_FIELD else local_soil_amount
                local_soil_amount = 0 if local_soil_amount < 0 else local_soil_amount
                positions[x - start_x][y - start_y] = local_soil_amount
                self.world.fields[id].insert_soil(local_soil_amount)
        for x in range(len(positions[0])):
            print()
            for y in range(len(positions[0])):
                print(f'{positions[x][y]:4.0f}', end=' ')


    def field_fill_circle(self, size, amount, offset_x=0.5, offset_y=0.5, grad=False, noise=False, noise_ampl=0.2):
        size = size -1 if size % 2 == 0 else size
        if size < 1:
            return
        size = min(size, cn.FIELDS_NUMBER_BY_SIDE)
        centr_x = floor(cn.FIELDS_NUMBER_BY_SIDE * offset_x)
        centr_y = floor(cn.FIELDS_NUMBER_BY_SIDE * offset_y)
        halfsize = floor(size / 2)
        start_x = centr_x - halfsize
        start_y = centr_y - halfsize
        end_x = centr_x + (size - halfsize)
        end_y = centr_y + (size - halfsize)

        start_x = 0 if start_x < 0 else start_x
        start_y = 0 if start_y < 0 else start_y
        end_x = cn.FIELDS_NUMBER_BY_SIDE if end_x > cn.FIELDS_NUMBER_BY_SIDE else end_x
        end_y = cn.FIELDS_NUMBER_BY_SIDE if end_y > cn.FIELDS_NUMBER_BY_SIDE else end_y

        shoulder = ceil(size / 2)
        delta = abs(amount - cn.INIT_SOIL) / shoulder if shoulder > 0 else 0

        print('=======================')
        print(f'размер: {size}, halfsize: {halfsize}')
        print(f'центр {centr_x},{centr_y}')
        print(f'верхний левый {start_x}, {start_y}')
        print(f'нижний правый {end_x}, {end_y}')
        print(f'плечо {shoulder}  дельта {halfsize}')
        positions = [[-1 for _ in range(start_x, end_x)] for _ in range(start_y, end_y)]

        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                hypo_delta = size/2- hypot(x - centr_x, y - centr_y)
                if hypo_delta > 0:
                    id = Field.coord_to_id(x, y)
                    local_soil_amount = amount
                    if grad:
                        reduse = int(hypot(x - centr_x, y - centr_y))
                        local_soil_amount = amount - delta * reduse

                    if noise:
                        local_soil_amount = local_soil_amount * (.5 + (random() - .5) * noise_ampl)

                    local_soil_amount = cn.MAX_SOIL_ON_FIELD if local_soil_amount > cn.MAX_SOIL_ON_FIELD else local_soil_amount
                    local_soil_amount = 0 if local_soil_amount < 0 else local_soil_amount
                    positions[x - start_x][y - start_y] = local_soil_amount
                    self.world.fields[id].insert_soil(local_soil_amount)
        for x in range(len(positions[0])):
            print()
            for y in range(len(positions[0])):
                print(f'{positions[x][y]:4.0f}', end=' ')
    def plant_fill_box(self, size, amount, offset_x=0.5, offset_y=0.5, grad=False):
        pass