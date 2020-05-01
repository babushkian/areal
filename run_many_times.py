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

    condit = [0, 30, 90, 180, 360, 720]
    for x in condit:
        cn.SEED_GROW_UP_CONDITION = x
        win = App()
        win.mainloop()
        if EXIT:
            break
# В конце каждого прохода надо выводить строку с метриками симуляции:
# - количество растений за время симуляции
# - вест биомассы за время симуляции
# - количество семян
# - процени проросших семян
