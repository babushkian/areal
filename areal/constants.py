﻿import math

RANDOM_ON = True
RANDOM_SEED = 'banana'

GRAPHICS = True # будет ли отображаться симуляция на экране

GRAPH_PLANT = True
GRAPH_SEED = True
GRAPH_FIELD = True

if not GRAPHICS:
    GRAPH_PLANT = False
    GRAPH_SEED = False
    GRAPH_FIELD = False

GRAPH_DICT = {  'plant': GRAPH_PLANT,
                'seed':GRAPH_SEED,
                'field': GRAPH_FIELD}




MONTHS = 24  # кличество тиков в одном году. позволяет настраивать плавность развития
MAX_WIDNDOW = 840 # максимальнный линейный размер игрового поля в пикселях
PHYS_SIZE = 100  # физические размеры игрового поля: +- 100 по обоим координатам
FIELD_SIZE_PIXELS = 128  # размер одной клетки в пикселях


FIELDS_NUMBER_BY_SIDE = 11 # размерность игрового поля в клетках (по одной стороне, так как поле квадратное)



# частота обновления кадолв. Вычисляется в ззависимости от нагрузки (в осоновном от размера поля)
BASE_DELAY = 1
def define_delay():
    AFTER_COOLDOWN = BASE_DELAY + 5 * GRAPH_FIELD + (1 * GRAPH_PLANT + 2 * GRAPH_SEED) \
                     * int(FIELDS_NUMBER_BY_SIDE * FIELDS_NUMBER_BY_SIDE /16)
    return AFTER_COOLDOWN


SIMULATION_PERIOD = 50  # количество лет, по истечении которых симуляция завершается



if FIELD_SIZE_PIXELS * FIELDS_NUMBER_BY_SIDE > MAX_WIDNDOW:
    FIELD_SIZE_PIXELS = MAX_WIDNDOW // FIELDS_NUMBER_BY_SIDE
WIDTH = FIELD_SIZE_PIXELS * FIELDS_NUMBER_BY_SIDE  # размеры окна в пикселях
HEIGHT = WIDTH  # поле квадратное, так что не паримся с лишними вычислениями
# физическое расстояние от центра игрового поля до угла. Нужна для определения суровости погоды,
# так как суровость распространяется радиально
PHYS_HYPOT = math.hypot(PHYS_SIZE, PHYS_SIZE)
# погодный угол, за год проходит все 360 градусов.
# А угол, потому что погодные условия вычисляются с использованием синуса
MONTS_ANGLE = math.pi * 2 / MONTHS



# цвета объектов
FRESH_PLANT_COLOR = 'lawn green'
SICK_PLANT_COLOR = 'forest green'#'dark olive green'
SEED_COLOR = 'goldenrod' #,'light goldenrod' #, 'light goldenrod yellow' , 'pale goldenrod' ,'gold'


# парамерты для отрисовки растений, семян и гнили
DRAW_PARAMS = {'plant':{'size':3, 'color': FRESH_PLANT_COLOR, 'border':1},
                'seed':{'size':2, 'color': SEED_COLOR, 'border':0}}

GLOBAL_COUNTER = 0
def global_counter():
    """
    Функция выдает индивидуальные номера для объектов на холсте когда графический
    режим отключен. В противном случае id создаются при создании графических объектов
    """
    global GLOBAL_COUNTER
    id = GLOBAL_COUNTER
    GLOBAL_COUNTER += 1
    return id

# РАСТЕНИЕ
PLANT_LIFETIME_YEARS = 4 # время жизни в годах
FRUITING_PERIOD = 0.5  # период между плодоношениями (в годах) . Чем меньше, тем чаще плодоношение.



# КЛЕТКА (класс Field )
INIT_SOIL = 80  # количество почвы на клетке
# чтобы количество почвы не улетало в бесконечность и графическое отображение на экране не крашилось
MAX_SOIL_ON_FIELD = 10000
# максимальное количество растений на клетку, чтобы симуляция не тормозила
MAX_PLANTS_IN_FIELD = 5
DECAY_HALFLIFE = 2*MONTHS * PLANT_LIFETIME_YEARS# за сколько ходов осдвется полвина гнили



# СЕМЯ
# условие проростания семечка. Сколько земли должно быть в клетке
SEED_GROW_UP_CONDITION = 20
# сколько лет семечко может пролежать до всхода и не умереть
SEED_LIFE = 5
# время, в течении которого семечко не прорастает (в годах)
SEED_PROHIBITED_GROW_UP = 2


# скрытая масса семечка, его внутренние резервы
SEED_HIDDEN_MASS = 5
#скорость исчерпания семечком внутренних резервов
SEED_FEED = SEED_HIDDEN_MASS/(SEED_LIFE * MONTHS)

# масса семечка
SEED_MASS = 1
TOTAL_SEED_MASS = SEED_MASS + SEED_HIDDEN_MASS
# вероятность перелететь в одну из соседних клеток
MIGRATION_PROB = 0.50


# максимальная масса растения
PLANT_MAX_MASS = 30

# логирование
WRITE_FIELDS_INFO = True
WRITE_PLANTS_INFO = True
WRITE_WORLD_INFO = True
