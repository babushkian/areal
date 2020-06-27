import os
from areal import constants as cn
from areal.world import World

w = World()
w.init_sim()
for i in range(150):
    print(w.global_time)
    w.time_pass()
    w.update()