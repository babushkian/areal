import sys
import ast
import configparser
from tkinter import *

from areal import world


def assign_world_const(modul, parc):
	for key in parc:
		gv = parc.get(key)
		#print("get value:", gv)
		try:
			x = ast.literal_eval(gv)
		except ValueError:
			x = gv
		#print("type: ", type(x))
		constant = key.upper()
		setattr(modul, constant, x)  # присавиваем атрибуты класса из конфига
		#print("Значение переменной",constant ,getattr(modul, constant))
	return None

# обработать случай отсутствия файла конфигурации

config = configparser.ConfigParser()
try:
	conf_file = open('areal.cfg', 'r', encoding='utf-16')
except:
	print('Отсутствует файл конфигурации.')
	sys.exit(1)

config.read_file(conf_file)
sect  = config.sections()
#for i in sys.modules:
#	print(i, ":", sys.modules[i])
modul = sys.modules['areal.world']
#print(modul)
assign_world_const(modul, config[sect[0]])
world.init_constants()

root = Tk()
world.World(root)
root.mainloop()
