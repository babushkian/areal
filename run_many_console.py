
import os
import time

from areal import constants as cn
from areal import heaven

cn.GRAPHICS = False

if __name__ == '__main__':
    soil = [220, 240,]
    condit = [40, 90]
    progib = [0, 0.5]
    life = [ 3, 5]
    heaven.init_sim_dir()
    heaven.init_metric()
    for v in soil:
        cn.INIT_SOIL = v
        for x in condit:
            cn.SEED_GROW_UP_CONDITION = x
            for y in progib:
                cn.SEED_PROHIBITED_GROW_UP = y
                for z in life:
                    cn.SEED_LIFE = z
                    w = heaven.Heaven(None, None)
                    w.init_sim()
                    while not w.game_over:
                        w.update()
