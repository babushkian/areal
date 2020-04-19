
from tkinter import *
from areal import world


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

    def __init__(self):
        super().__init__()
        self.sim_state = False
        self.stars = []
        self.labels = []
        self.interface_build()
        self.update()

    def interface_build(self):
        self.title("Ареал")
        self.minsize(900, 760)
        # нарезаем окно на зоны
        self.bottom_frame = Frame(self, relief=GROOVE, borderwidth=2, padx=3, pady=3)
        self.bottom_frame.pack(side=BOTTOM, expand=YES, fill=X)

        self.rightframe = Frame(self.bottom_frame, relief=GROOVE, borderwidth=2, padx=5, pady=5)

        self.canvframe = Frame(self.bottom_frame, relief=GROOVE, borderwidth=2, padx=5, pady=5)
        self.canvframe.pack(side=LEFT)
        self.rightframe.pack(side=RIGHT, expand=YES, fill=X)

        # в левой зоне рисуем канвас
        self.canv = world.World(self.canvframe, self)
        self.canv.pack()

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

    def update(self):
        if self.canv.newborn:
            self.statrtbutton.config(text='СТАРТ')
        elif self.sim_state == False:
            self.statrtbutton.config(text='ПРОДОЛЖИТЬ')
        else:
            self.statrtbutton.config(text='ОСТАНОВИТЬ')
        self.after(15, self.update)
        if self.canv.world_mass == 0:
            plant_percent = seed_percent = rot_percent = soil_percent = 0
        else:
            plant_percent = self.canv.plant_mass / self.canv.world_mass *100
            seed_percent = self.canv.seed_mass / self.canv.world_mass *100
            rot_percent = self.canv.rot_mass / self.canv.world_mass * 100
            soil_percent = self.canv.soil_mass / self.canv.world_mass * 100

        data = (self.canv.global_time,
                self.canv.plant_num,
                self.canv.starving_percent,
                self.canv.seed_num,
                self.canv.rot_num,
                plant_percent,
                seed_percent,
                rot_percent,
                soil_percent)
        for no, lab in enumerate(self.labels):
            lab.config(text=self.LABELS_TEXT[no].format(data[no]))


    def one_step(self):
        self.sim_state = False
        self.canv.run()

    def start_stop(self):
        if self.sim_state == False:
            self.sim_state = True
            self.canv.run()
        else:
            self.sim_state = False


    def restart(self):
        self.sim_state = False
        for star in self.stars:
            self.canv.delete(star)
        self.stars = []
        self.canv.destroy()
        self.canv = world.World(self.canvframe, self)
        self.canv.pack()


    def quit(self):
        self.destroy()


if __name__ == '__main__':
    win = App()
    win.mainloop()
