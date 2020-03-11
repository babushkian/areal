import configparser
config = configparser.ConfigParser()
config.add_section('main_window')


config.set('main_window', 'MONTS', str(16))  # кличество тиков в одном году. позволяет настраивать плавность развития
config.set('main_window', 'MAX_WIDNDOW',  str(960)) # максимальная высота игрового поля в пикселях
config.set('main_window', 'DIMENSION', str(100))  # прространственная размерность: +- 100 по обоим координатам
config.set('main_window', 'CHECK_DIM', str(48))  # размер одной клетки в пикселях
config.set('main_window', 'DRAW_DIM',  str(15))  # размерность поля в клетках

with open('areal.cfg', 'w', encoding = 'utf-16') as configfile: 
	config.write(configfile)
