import os
from areal import constants as cn
from areal import heaven

w = heaven.Heaven(None)
w.init_sim()
while not w.game_over:
    w.update()

