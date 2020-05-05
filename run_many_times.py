from tkinter import *
import os
import time
from main import InfoLabels
from areal import world
from areal import constants as cn
from areal import draw_fig

EXIT = False # пр нажатии на эсекйп становится истиной и происходит выход из симуляции

class App(Tk):
    def __init__(self, sim_dir, img_dir, metr):
        super().__init__()
        self.series = True # серия симуляций
        self.sim_state = True
        self.sim_dir = sim_dir
        self.img_dir = img_dir
        self.metr_file = metr

        self.bind('<Escape>', self.cancel_sim)
        self.canv = world.World(self, self)
        if os.path.getsize(self.metr_file.name) == 0:
            self.canv.population_metric_head(self.metr_file)
        self.labelframe = InfoLabels(self, self)
        self.update_a()
        self.canv.init_sim()
        self.canv.update_a()

    def update_a(self):
        if self.canv.game_over:
            self.draw_figure()
            self.destroy()
        else:
            self.labelframe.update_a()
            self.after(1, self.update_a)

    def draw_figure(self):
        for file in self.canv.log_functions:
            draw_fig.draw_pic(os.path.abspath(file.name), self.img_dir)

    def is_draw(self, obj):
        return False

    def cancel_sim(self, event = None):
        global EXIT
        if event:
            EXIT = True
        del self.canv
        self.destroy()

if __name__ == '__main__':
    soil = [220, 240, 260, 280]
    condit = [0, 40, 90, 160, 200, 240]
    progib = [0, 0.5, 1.5, 3]
    life = [1, 3, 5, 7]


    cur_date = time.time()
    sim_dir = 'sim_' + time.strftime("%d.%m.%Y_%H.%M.%S", time.localtime(cur_date))
    os.mkdir(sim_dir)
    img_dir = os.path.join(sim_dir, 'figures')
    os.mkdir(img_dir)
    metr = os.path.join(sim_dir, 'metric.csv')
    metr = open(metr, 'w', encoding='UTF16')
    for v in soil:
        cn.INIT_SOIL = v
        for x in condit:
            cn.SEED_GROW_UP_CONDITION = x
            for y in progib:
                cn.SEED_PROHIBITED_GROW_UP = y
                for z in life:
                    cn.SEED_LIFE = z
                    win = App(sim_dir, img_dir, metr)
                    win.mainloop()
                    if EXIT:
                        break
                if EXIT:
                    break
            if EXIT:
                break
        if EXIT:
            break
