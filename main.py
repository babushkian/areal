import random
from tkinter import *
from areal import constants as cn
from areal import world
from areal.plant import Plant
from areal.seed import Seed
from areal.rot import Rot
# для эксперимента у всех констант будут единичные значения, а потом эти константы будут загружаться из конфига

class App(Tk):
    LABELS_TEXT = ['цикл:{:5d}',
                   'растений:{:5d}',
                   'голодающих:{:5.1f}%',
                   'семян:{:5d}',
                   'гнили:{:5d}',
                   'масса растений:{:5.1f}%',
                   'масса семян:{:5.1f}%',
                   'масса гнили:{:5.1f}%',
                   'масса почвы:{:5.1f}%']

    CHECKBOX_TEXT = {'plant': 'рисотвать растения    ',
                  'seed': 'рисовать семена        ',
                  'rot': 'рисовать гниль            ',
                  'field': 'рисовать клетки поля'}
    CHECKS = {}
    def __init__(self):
        super().__init__()
        self.sim_state = False
        self.stars = []
        self.labels = []
        self.interface_build()
        self.bind('<Escape>', self.restart)
        self.bind('<space>', self.start_stop)
        self.bind('<Right>', self.one_step)
        self.update()
        self.restart()

    def interface_build(self):
        self.title("Ареал")
        self.minsize(1000, 760)
        # нарезаем окно на зоны
        self.bottom_frame = Frame(self, relief=GROOVE, borderwidth=2, padx=3, pady=3)
        self.bottom_frame.pack(side=BOTTOM, expand=YES, fill=X)

        self.rightframe = Frame(self.bottom_frame, relief=GROOVE, borderwidth=2, padx=3, pady=3)

        self.canvframe = Frame(self.bottom_frame, relief=GROOVE, borderwidth=2, padx=3, pady=3)
        self.canvframe.pack(side=LEFT)
        self.rightframe.pack(side=RIGHT, expand=YES, fill=X)

        # в левой зоне рисуем канвас
        self.canv = world.World(self.canvframe, self)
        self.canv.pack()

        # делаем чекбоксы
        self.right_up_frame = Frame(self.rightframe, relief=GROOVE, borderwidth=2, padx=3, pady=3)
        self.right_up_frame.pack(side=TOP, expand=YES, fill=X)
        for ch in self.CHECKBOX_TEXT:
            check_var = IntVar(value=cn.GRAPH_DICT[ch])
            c = Checkbutton(self.right_up_frame, variable=check_var, text=self.CHECKBOX_TEXT[ch])
            c.pack(side=TOP, expand=YES, fill=X)
            self.CHECKS[ch] = (c, check_var)
        for ch in self.CHECKS:
            print(ch, self.CHECKS[ch][1], self.CHECKS[ch][0])
            if self.CHECKS[ch][1].get() == 1:
                self.CHECKS[ch][0].select()
            else:
                self.CHECKS[ch][0].deselect()

        # в правой зоне рисуем текстовое поле и кнопки
        self.resetbutton = Button(self.rightframe, text='СБРОС', command=self.restart)
        self.statrtbutton = Button(self.rightframe, text='INIT', command=self.start_stop)
        self.one_step_button = Button(self.rightframe, text='ШАГ ВПЕРЕД >>>', command=self.one_step)
        self.quitbutton = Button(self.rightframe, text='ВЫХОД', command=self.quit)

        self.quitbutton.pack(side=BOTTOM, expand=YES, fill=X)
        self.one_step_button.pack(side=BOTTOM, expand=YES, fill=X)
        self.statrtbutton.pack(side=BOTTOM, expand=YES, fill=X)
        self.resetbutton.pack(side=BOTTOM, expand=YES, fill=X)

        self.labelframe = Frame(self.rightframe, relief=GROOVE, borderwidth=2, padx=8, pady=8)
        self.labelframe.pack(side=TOP, expand=YES, fill=X)
        # наполняем верхнюю зону надписями
        for i in range(len(self.LABELS_TEXT)):
            a = Label(self.labelframe, width=23, text=self.LABELS_TEXT[i].format(0), anchor=NW)
            a.pack(side=TOP)
            self.labels.append(a)

        print(self.CHECKS)
        print(App.CHECKS)

    def update(self):
        if self.canv.newborn:
            self.statrtbutton.config(text='СТАРТ')
        elif self.sim_state == False:
            self.statrtbutton.config(text='ПРОДОЛЖИТЬ')
        else:
            self.statrtbutton.config(text='ОСТАНОВИТЬ')

        if self.canv.world_mass == 0:
            plant_percent = seed_percent = rot_percent = soil_percent = 0
        else:
            plant_percent = self.canv.plant_mass / self.canv.world_mass *100
            seed_percent = self.canv.seed_mass / self.canv.world_mass *100
            rot_percent = self.canv.rot_mass / self.canv.world_mass * 100
            soil_percent = self.canv.soil_mass / self.canv.world_mass * 100

        data = (self.canv.global_time,
                Plant.COUNT,
                self.canv.starving_percent,
                Seed.COUNT,
                Rot.COUNT,
                plant_percent,
                seed_percent,
                rot_percent,
                soil_percent)
        for no, lab in enumerate(self.labels):
            lab.config(text=self.LABELS_TEXT[no].format(data[no]))
        self.after(10, self.update)

    def test_del_tag(self):
        self.canv.delete('plant') # удяляет все объекты с выделенным тегом, функция ничего не возвращает

    def one_step(self, event=None):
        self.sim_state = False
        self.disable_checkbutton()
        self.canv.run()

    def start_stop(self, event=None):
        if self.sim_state == False:
            self.sim_state = True
            self.disable_checkbutton()
            self.canv.run()
        else:
            self.sim_state = False

    def disable_checkbutton(self):
        for x in self.CHECKS:
            self.CHECKS[x][0].config(state = DISABLED)
            #cn.GRAPH_DICT[x] = self.CHECKS[x][1].get()

    def enable_checkbutton(self):
        for x in self.CHECKS:
            self.CHECKS[x][0].config(state = NORMAL)


    def restart(self, event=None):
        random.seed(666)
        self.sim_state = False
        self.enable_checkbutton()
        self.canv.destroy()
        self.canv = world.World(self.canvframe, self)
        self.canv.pack()


    def quit(self):
        self.destroy()


if __name__ == '__main__':
    win = App()
    win.mainloop()
