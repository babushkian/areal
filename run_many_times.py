import os
import time

from areal import world
from areal import constants as cn

soil = [220, 240, 260, 280]
condit = [0, 40, 90, 160, 200, 240]
progib = [0, 0.5, 1.5, 3]
life = [1, 3, 5, 7]

cur_date = time.time()
sim_dir = 'sim_' + time.strftime("%d.%m.%Y_%H.%M.%S", time.localtime(cur_date))
os.mkdir(sim_dir)
metr = os.path.join(sim_dir, 'metric.csv')
metr_file = open(metr, 'w', encoding='UTF16')
count = 0
for v in soil:
    cn.INIT_SOIL = v
    for x in condit:
        cn.SEED_GROW_UP_CONDITION = x
        for y in progib:
            cn.SEED_PROHIBITED_GROW_UP = y
            for z in life:
                cn.SEED_LIFE = z
                count +=1
                print(f'NUM: {count:4}\tsoil:{v:4}\tcondition:\t{v:4} prohibit: {y:4}\tlife: {z:4}')
                w = world.World(sim_dir , metr_file)
                if os.path.getsize(metr_file.name) == 0:
                    w.population_metric_head(metr_file)
                w.init_sim()
                while not w.game_over:
                    w.update_a()

