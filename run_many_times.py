from tkinter import *
from main import InfoLabels
from areal import world
from areal import constants as cn

EXIT = False
#cn.GRAPHICS = False

class App(Tk):
    def __init__(self):
        super().__init__()
        self.sim_state = True
        self.bind('<Escape>', self.cancel_sim)
        self.canv = world.World(self, self)
        self.labelframe = InfoLabels(self, self)
        self.update_a()
        self.canv.init_sim()
        self.canv.update_a()

    def update_a(self):
        if self.canv.game_over:
            self.destroy()
        else:
            self.labelframe.update_a()
            self.after(1, self.update_a)

    def is_draw(self, obj):
        return False

    def cancel_sim(self, event = None):
        global EXIT
        if event:
            EXIT = True
        del self.canv
        self.destroy()


if __name__ == '__main__':

    condit = [0, 80, 160, 320, 410, 460]
    progib = [0, .5, 1.3, 3, 4]
    life = [1, 3, 5, 7]

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
# В конце каждого прохода надо выводить строку с метриками симуляции:
# - количество растений за время симуляции
# - вест биомассы за время симуляции
# - количество семян
# - процени проросших семян
