import os
import random

from tkinter import *

from areal import heaven
from areal import constants as cn
from areal.help import HelpButton
from areal.plant import Plant
from areal.seed import Seed


class App(Tk):
    def __init__(self):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.series = True  # единичная симуляция, а не серия
        self.sim_state = False
        self.newborn = True
        self.world_timer = None # таймер обновления мира
        self.interface_build()
        self.bind('<Escape>', self.restart)
        self.bind('<space>', self.start_stop)
        self.bind('<Right>', self.one_step)
        self.update_a()
        self.restart()

    def interface_build(self):
        self.title("Ареал 022")
        self.minsize(1000, 760)
        self.canvframe = Frame(self, relief=GROOVE, borderwidth=2, padx=3, pady=3)
        self.canvframe.pack(side=LEFT)
        self.canv = heaven.Heaven(self.canvframe, self) #parent(фрейм,куда будет встроен холст)

        self.rightframe = Frame(self, relief=GROOVE, borderwidth=2, padx=3, pady=3)
        self.rightframe.pack(side=RIGHT, expand=YES, fill=BOTH)
        self.right_up_frame = Frame(self.rightframe, relief=GROOVE, borderwidth=2, padx=3, pady=3)
        self.right_up_frame.pack(side=TOP, expand=YES, fill=X)
        HelpButton(self.right_up_frame)
        self.rand_label = Label(self.right_up_frame, text='Сид генератора случайных чисел')
        self.rand_label.pack(side=TOP)
        self.random_var = StringVar(value=cn.RANDOM_SEED)
        self.entry = Entry(self.right_up_frame,  textvariable = self.random_var)
        self.entry.pack(side=TOP, expand=YES, fill=X)

        self.chbox = Checkers(self.rightframe, self)
        self.labelframe = InfoLabels(self.rightframe, self)
        self.buttons = Buttons(self.rightframe, self)


    def update_a(self):
        self.buttons.update_a()
        self.labelframe.update_a()
        self.after(20, self.update_a)

    def init_if_newborn(self):
        if self.newborn:
            print('Инициализировали')
            self.canv.init_sim()
            self.newborn = False

    def simulate(self):
        self.canv.update()
        if self.sim_state:
            self.world_timer = self.after(20, self.simulate)
        else:
            if self.world_timer:
                self.after_cancel(self.world_timer)

    def one_step(self, event=None):
        self.init_if_newborn()
        self.chbox.disable_checkbutton()
        self.simulate()

    def start_stop(self, event=None):
        self.init_if_newborn()
        if not self.canv.game_over:
            if self.sim_state == False:
                self.sim_state = True
                self.chbox.disable_checkbutton()
                self.simulate()
            else:
                self.sim_state = False

    def restart(self, event=None):
        if self.world_timer:
            self.after_cancel(self.world_timer)
        if cn.RANDOM_ON:
            self.entry.config(state=DISABLED)
            self.rand_label.config(text='Генератор истинно случайных чисел.')
        else:
            random.seed(self.random_var.get())
        self.sim_state = False
        self.chbox.enable_checkbutton()
        if not self.newborn:
            self.canv.end_of_simulation()
            self.canv.delete_simulation()
            del self.canv
            self.canv = heaven.Heaven(self.canvframe, self)
            self.newborn = True


    def is_draw(self, objname):
        return self.chbox.is_draw(objname)

    def quit(self):
        if not self.newborn:
            self.canv.end_of_simulation()
        del self.canv
        print("Удаляем мир и окно")
        self.destroy()

class Checkers(Frame):
    CHECKBOX_TEXT = {'plant': 'рисотвать растения    ',
                  'seed': 'рисовать семена        ',
                  'field': 'рисовать клетки поля'}
    CHECKS = {}
    def __init__(self, root, app):
        self.app = app
        super().__init__(root, relief=GROOVE, borderwidth=2, padx=3, pady=3)
        self.pack(side=TOP, expand=YES, fill=X)
        for ch in self.CHECKBOX_TEXT:
            check_var = IntVar(value=cn.GRAPH_DICT[ch])
            c = Checkbutton(self, variable=check_var, text=self.CHECKBOX_TEXT[ch])
            c.pack(side=TOP, expand=YES, fill=X)
            self.CHECKS[ch] = (c, check_var)
        for ch in self.CHECKS:
            if self.CHECKS[ch][1].get() == 1:
                self.CHECKS[ch][0].select()
            else:
                self.CHECKS[ch][0].deselect()

    def disable_checkbutton(self):
        for x in self.CHECKS:
            self.CHECKS[x][0].config(state=DISABLED)

    def enable_checkbutton(self):
        for x in self.CHECKS:
            self.CHECKS[x][0].config(state=NORMAL)

    def is_draw(self, objname):
        return Checkers.CHECKS[objname][1].get()


class InfoLabels(Frame):
    LABELS_TEXT = ['цикл:{:5d}',
                   'растений:{:5d}',
                   'голодающих:{:5.1f}%',
                   'семян:{:5d}',
                   'масса растений:{:5.1f}%',
                   'масса семян:{:5.1f}%',
                   'масса гнили:{:5.1f}%',
                   'масса почвы:{:5.1f}%']

    def __init__(self, root, app):
        self.app = app
        self.labels = []
        super().__init__(root, relief=GROOVE, borderwidth=2, padx=3, pady=3)
        self.pack(side=TOP, expand=YES, fill=X)
        for i in range(len(self.LABELS_TEXT)):
            a = Label(self, width=23, text=self.LABELS_TEXT[i].format(0), anchor=NW)
            a.pack(side=TOP)
            self.labels.append(a)

    def update_a(self):
        if self.app.canv.world_mass == 0:
            plant_percent = seed_percent = rot_percent = soil_percent = 0
            starving = time = 0
            #print("ZERO")
        else:
            plant_percent = self.app.canv.plant_mass / self.app.canv.world_mass * 100
            seed_percent = self.app.canv.seed_mass / self.app.canv.world_mass * 100
            rot_percent = self.app.canv.rot_mass / self.app.canv.world_mass * 100
            soil_percent = self.app.canv.soil_mass / self.app.canv.world_mass * 100
            time = self.app.canv.world.global_time
            starving = self.app.canv.starving_percent
        data = (time,
                Plant.COUNT,
                starving,
                Seed.COUNT,
                plant_percent,
                seed_percent,
                rot_percent,
                soil_percent)
        for no, lab in enumerate(self.labels):
            lab.config(text=self.LABELS_TEXT[no].format(data[no]))


class Buttons(Frame):
    def __init__(self, root, app):
        self.app = app
        super().__init__(root, relief=GROOVE, borderwidth=2, padx=3, pady=3)
        self.pack(side=TOP, expand=YES, fill=X)
        # в правой зоне рисуем текстовое поле и кнопки
        self.reset_button = Button(self, text='СБРОС', command=self.restart)
        self.statrt_button = Button(self, text='INIT', command=self.start_stop)
        self.one_step_button = Button(self, text='ШАГ ВПЕРЕД >>>', command=self.one_step)
        self.quit_button = Button(self, text='ВЫХОД', command=self.app.quit)

        self.quit_button.pack(side=BOTTOM, expand=YES, fill=X)
        self.one_step_button.pack(side=BOTTOM, expand=YES, fill=X)
        self.statrt_button.pack(side=BOTTOM, expand=YES, fill=X)
        self.reset_button.pack(side=BOTTOM, expand=YES, fill=X)

    def update_a(self):
        if self.app.newborn:
            self.statrt_button.config(text='СТАРТ')
        elif self.app.sim_state == False:
            self.statrt_button.config(text='ПРОДОЛЖИТЬ')
        else:
            self.statrt_button.config(text='ОСТАНОВИТЬ')

    def one_step(self, event=None):
        self.app.one_step()

    def start_stop(self, event=None):
        self.app.start_stop()

    def restart(self, event=None):
        self.app.restart()

if __name__ == '__main__':
    heaven.init_sim_dir()
    heaven.init_metric()
    win = App()
    win.mainloop()
