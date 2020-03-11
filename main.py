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


config = configparser.ConfigParser()
config.read('areal.cfg', encoding ='utf-16')
sect  = config.sections()
for i in sys.modules:
	print(i, ":", sys.modules[i])
modul = sys.modules['areal.world']
#print(modul)
assign_world_const(modul, config[sect[0]])
world.init_constants()

root = Tk()
world.World(root)
root.mainloop()
