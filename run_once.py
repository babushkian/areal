import os
from areal import constants as cn
from areal import heaven
cn.GRAPHICS = False
heaven.init_sim_dir()
heaven.init_metric()
w = heaven.Heaven(None, None)
w.init_sim()
while not w.game_over:
    w.update()

