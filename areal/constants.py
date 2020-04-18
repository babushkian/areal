import math

GRAPHICS = False # будет ли отображаться симуляция на экране
SIMULATION_PERIOD = 400  # количество лет, по истечении которых симуляция завершается



MONTHS = 24  # кличество тиков в одном году. позволяет настраивать плавность развития
MAX_WIDNDOW = 720 # максимальнный линейный размер игрового поля в пикселях
PHYS_SIZE = 100  # физические размеры игрового поля: +- 100 по обоим координатам
FIELD_SIZE_PIXELS = 48  # размер одной клетки в пикселях
FIELDS_NUMBER_BY_SIDE = 15  # размерность игрового поля в клетках (по одной стороне, так как поле квадратное)


if FIELD_SIZE_PIXELS * FIELDS_NUMBER_BY_SIDE > MAX_WIDNDOW:
    FIELD_SIZE_PIXELS = MAX_WIDNDOW // FIELDS_NUMBER_BY_SIDE
WIDTH = FIELD_SIZE_PIXELS * FIELDS_NUMBER_BY_SIDE  # размеры окна в пикселях
HEIGHT = WIDTH # поле квадратное, так что не паримся с лишними вычислениями
# физическое расстояние от центра игрового поля до угла. Нужна для определения суровости погоды,
# так как суровость распространяется радиально
PHYS_HYPOT = math.hypot(PHYS_SIZE, PHYS_SIZE)
# погодный угол, за год проходит все 360 градусов.
# А угол, потому что погодные условия вычисляются с использованием синуса
MONTS_ANGLE = math.pi * 2 / MONTHS

# цвета объектов
FRESH_PLANT_COLOR = 'lawn green'
SICK_PLANT_COLOR = 'dark olive green'
SEED_COLOR = 'goldenrod' #,'light goldenrod' #, 'light goldenrod yellow' , 'pale goldenrod' ,'gold'
ROT_COLOR = 'saddle brown'

# КЛЕТКА (класс Field )
INIT_SOIL = 900  # количество почвы на клетке
# максимальное количество растений на клетку, чтобы симуляция не тормозила
MAX_PLANTS_IN_FIELD = 5

# ГНИЛЬ
DECAY_MULTIPLIER = 0.3 # скорость гниения, гем больше, тем быстрее пасиение сгнивает

# СЕМЯ
# условие проростания семечка. Сколько земли должно быть в клетке
SEED_GROW_UP_CONDITION = 50
# сколько лет семечко может пролежать до всхода и не умереть
SEED_LIFE = 5
# время, в течении которого семечко не прорастает (в годах)
SEED_PROHIBITED_GROW_UP = 2

# РАСТЕНИЕ
PLANT_LIFETIME_YEARS = 4 # количество циклов
FRUITING_PERIOD = 0.25  # период размножения - в виде процента от года

# скрытая масса семечка, его внутренние резервы
PLANT_START_CONSUMED = 5
# масса семечка
SEED_MASS = 1
# максимальная масса растения
PLANT_MAX_MASS = 30

