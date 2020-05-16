from tkinter import *
from tkinter import font
import math
from areal import constants as cn
from areal.world import World
from areal.label import CanvasTooltip

class GW(Canvas):
    def __init__(self, parent, app):
        super().__init__(parent, width=cn.WIDTH, heigh=cn.HEIGHT, bg='gray50')
        self.pack()
        self.app = app
        self.wld = World(app)
        self.newborn = True  # смиуляция только создана и еще не запускалась
        self.game_over  = False # симуляция закончена по той или иной причине
        self.time_over = False # истек срок симуляции
        self.perish = False # все вымерли
        self.show_end = False # выводилась ли надпись об окончании игры
        self.fields = dict() # сожержит кортежи из объекта клетки на экране и объекта всплывающей подсказки к этой клетке
        # ключом служит объект физической клетки
        self.objects_on_screen = dict() # ключ: объект, который надо нарисовать, значение номер объекта на холсте

    def init_sim(self):
        self.wld.init_sim()
        self.create_fields()
        self.create_objects()
        self.newborn = False
        self.delay = cn.define_delay()


    def create_fields(self):
        if self.app.is_draw('field'):
            cd = cn.FIELD_SIZE_PIXELS
            for row in range(cn.FIELDS_NUMBER_BY_SIDE):
                for col in range(cn.FIELDS_NUMBER_BY_SIDE):
                    field = self.wld.fields[row][col]
                    shape = self.create_rectangle(cd * row, cd * col,
                                                      cd * row + cd, cd * col + cd,
                                                      width=0, fill='#888888', tags = field.name)
                    tooltip = CanvasTooltip(self, shape, text=self.create_tooltip_text(field))
                    self.fields[field] = (shape, tooltip)

    def create_objects(self):
        for o in self.wld.change_scene['new']:
            if self.app.is_draw(o.name):
                (size, color, border) = cn.DRAW_PARAMS[o.name].values()
                being =  self.create_rectangle(o.sx - size, o.sy - size,
                                               o.sx + size, o.sy + size,
                                               fill=color, width=border, tags=o.name)
                self.objects_on_screen[o] = being

    def delete_objects(self):
        for o in self.wld.change_scene['obsolete']:
            if self.app.is_draw(o.name):
                self.delete(self.objects_on_screen[o])

    def update_objects(self):
        self.delete_objects()
        self.create_objects()
        for obj in self.objects_on_screen:
            if obj.name == 'plant':
                color = cn.SICK_PLANT_COLOR if obj.delta < 0 else cn.FRESH_PLANT_COLOR
                self.itemconfig(self.objects_on_screen[obj], fill=color)

    def update_a(self):
        self.wld.update()
        self.update_fields()
        self.update_objects()

        self.tag_raise('plant')
        self.check_end_of_simulation()
        if not self.game_over:
            if self.app.sim_state:
                self.after(self.delay, self.update_a)
        else:
            self.end_of_simulation()

    def check_end_of_simulation(self):
        if not self.wld.global_time < cn.MONTHS * cn.SIMULATION_PERIOD:
            self.time_over = True
            self.game_over = True
        if self.wld.count_of_world_objects < 1:
            self.perish = True
            self.game_over = True


    def end_of_simulation(self):
        self.show_end = True

        if cn.GRAPHICS:
            bigfont = font.Font(family='arial', size=20, weight="bold")
            if self.time_over:
                self.create_text(360, 360, text='НАСТУПИЛА ПРЕДЕЛЬНАЯ ДАТА СИМУЛЯЦИИ', font=bigfont, fill='blue')
            if self.perish:
                self.create_text(360, 400, text='ПОПУЛЯЦИЯ ВЫМЕРЛА', font=bigfont, fill='blue')
        self.wld.population_metric_record(self.app.metr_file)
        self.app.metr_file.flush()
        self.wld.db.close_connection()
        self.wld.logging_close()


    def update_fields(self):
        def soil_color(field):
            t = int(7 * math.log2(field.soil + 1))
            return f'gray{t}'

        if self.app.is_draw('field'):
            for field in self.fields: # итерация по объектам клеток
                if cn.GRAPH_FIELD:
                    back = soil_color(field) # объект клетки к качестве параметра
                    self.itemconfigure(self.fields[field][0], fill=back)
                    self.fields[field][1].text = self.create_tooltip_text(field) #подсказка привязанная к клетке


    def create_tooltip_text(self, field):
        text = f'Клетка: {field.row:02d}x{field.col:02d}\n'
        text += f'Растений: {field.counts["plant"]:4d}({field.plant_mass:6.1f})\n'
        text += f'Семян: {field.counts["seed"]:4d}({field.seed_mass:6.1f})\n'
        text += f'Гнили: {field.counts["rot"]:4d}({field.rot_mass:6.1f})\n'
        text += f'Масса почвы: {field.soil:6.1f}'
        return text
    # в момент, когда графическией элемент удаляется, а подсказка была активирована, подтсказка
    # остается висеть навсегда, потому что не срабатывает обработчик выхода из поля объекта - его нет.

    def destroy(self):
        # чтобы после сброса симуляции не оставались открытые подсказки
        if CanvasTooltip.OPENED:
            for lab in CanvasTooltip.OPENED:
                lab.hide()

        super().destroy()
