from tkinter import *
import os
import time
from areal import graphics
from areal import heaven
from areal import constants as cn
from areal import draw_fig

EXIT = False # пр нажатии на эсекйп становится истиной и происходит выход из симуляции

class App(Tk):
    def __init__(self):
        super().__init__()
        self.series = True # серия симуляций
        self.sim_state = True


        self.bind('<Escape>', self.cancel_sim)
        self.hvn = heaven.Heaven(self, self) #parent(фрейм,куда будет встроен холст), app
        self.hvn.init_sim()
        self.hvn.update()
        self.update_a()


    def update_a(self):
        if self.hvn.game_over:
            #self.draw_figure()
            self.destroy()
        else:
            self.after(10, self.update_a)
            self.hvn.update()

    def draw_figure(self):
        for file in self.hvn.logging.log_functions:
            draw_fig.draw_pic(os.path.abspath(file.name), self.img_dir)

    def is_draw(self, obj):
        return True

    def cancel_sim(self, event = None):
        global EXIT
        if event:
            EXIT = True
        del self.hvn
        self.destroy()

if __name__ == '__main__':
    soil = [220, 240, 260, 280]
    condit = [0, 40, 90, 160, 200, 240]
    progib = [0, 0.5, 1.5, 3]
    life = [1, 3, 5, 7]

    soil = [240]
    condit = [40]
    progib = [0]
    life = [7]

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
                    win = App()
                    win.mainloop()
                    if EXIT:
                        break
                if EXIT:
                    break
            if EXIT:
                break
        if EXIT:
            break
