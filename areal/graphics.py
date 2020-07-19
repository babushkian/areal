from tkinter import *
from tkinter import font
import math
from areal import constants as cn
from areal.label import CanvasTooltip

class GW(Canvas):
    def __init__(self, hvn):
        self.hvn = hvn
        self.app = self.hvn.app
        self.update_event = None

        super().__init__(self.hvn.frame, width=cn.WIDTH, heigh=cn.HEIGHT, bg='gray50')
        self.pack()

        self.is_draw = None
        self.show_end = False # выводилась ли надпись об окончании игры
        self.fields = dict() # сожержит кортежи из объекта клетки на экране и объекта всплывающей подсказки к этой клетке
        # ключом служит объект физической клетки
        self.objects_on_screen = dict() # ключ: объект, который надо нарисовать, значение номер объекта на холсте

    def init_sim(self):
        self.is_draw = self.draw_or_not() # какие из элементов симуляции рисуются
        self.create_fields()
        self.create_objects()
        self.delay = cn.define_delay()
        self.update_event = self.after(self.delay, self.update_a)


    def draw_or_not(self):
        d = dict()
        for i in cn.GRAPH_DICT:
            d[i] = self.app.is_draw(i)
        return d

    def create_fields(self):
        if self.is_draw['field']:
            cd = cn.FIELD_SIZE_PIXELS
            for field in self.hvn.world.fields.values():
                shape = self.create_rectangle(cd * field.row, cd * field.col,
                                                  cd * field.row + cd, cd * field.col + cd,
                                                  width=0, fill='#888888', tags = field.name)
                tooltip = CanvasTooltip(self, shape, text=self.create_tooltip_text(field))
                self.fields[field] = (shape, tooltip)

    def create_objects(self):
        for o in self.hvn.world.change_scene['new'].values():
            if self.is_draw[o.name]:
                (size, color, border) = cn.DRAW_PARAMS[o.name].values()
                being =  self.create_rectangle(o.sx - size, o.sy - size,
                                               o.sx + size, o.sy + size,
                                               fill=color, width=border, tags=o.name)
                self.objects_on_screen[o] = being


    def delete_objects(self):
        for obj in self.hvn.world.change_scene['obsolete'].values():
            if self.is_draw[obj.name]:
                self.delete(self.objects_on_screen[obj])
                del self.objects_on_screen[obj]

    def update_objects(self):
        # обьекты так обрабатывабтся, что когда дело доходит до их отрисовки оним могут попасть в списки для
        # прорисовки и для удаления. Это происходит, когда растение отбрасываетс семечко, а оно на благоприятной
        # почве стразу прорастает. И так получается, что объект семечки создался и тут же уничтожился. И таким
        # образом попал в оба списка. Та как у меня сначала уничтожаются устаревшие объекты, то на уничтожение
        # отправляются объекты, которые не были нарисованы. Поэтому надо проверять - если объект попал в оба
        # списка, он просто удаляется из списка на прорисовку в методе удаления нарисованных объектов.
        self.delete_objects()
        self.create_objects()
        for obj in self.objects_on_screen:
            if obj.name == 'plant':
                color = cn.SICK_PLANT_COLOR if obj.delta < 0 else cn.FRESH_PLANT_COLOR
                self.itemconfig(self.objects_on_screen[obj], fill=color)

    def update_fields(self):
        def soil_color(field):
            t = int(7 * math.log2(field.soil + 1))
            if t > 99:
                t = 99
            return f'gray{t}'

        if self.is_draw['field']:
            for field in self.fields: # итерация по объектам клеток
                back = soil_color(field) # объект клетки к качестве параметра
                self.itemconfigure(self.fields[field][0], fill=back)
                self.fields[field][1].text = self.create_tooltip_text(field) #подсказка привязанная к клетке

    def update_a(self):
        print('Обновление графики')
        print(self.hvn.world.global_time)
        if self.hvn.calculated:
            self.update_fields()
            self.update_objects()
            self.tag_raise('plant')
            self.hvn.calculated = False
        self.update_event = self.after(self.delay, self.update_a)


    def display_end_of_simulation(self):
        self.show_end = True
        if self.update_event:
            self.after_cancel(self.update_event)
        bigfont = font.Font(family='arial', size=20, weight="bold")
        if self.hvn.time_over:
            self.create_text(360, 360, text='НАСТУПИЛА ПРЕДЕЛЬНАЯ ДАТА СИМУЛЯЦИИ', font=bigfont, fill='blue')
        if self.hvn.perish:
            self.create_text(360, 400, text='ПОПУЛЯЦИЯ ВЫМЕРЛА', font=bigfont, fill='blue')


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
