import csv
import os
import re
import matplotlib.pyplot as plt
from areal.constants import FIELDS_NUMBER_BY_SIDE

seed_color = '#ffe443'
plant_color = '#9ec866'
soil_color = '#c7ac7d'
rot_color =   '#9d7651'

def parse_filename(filename):
	template = r'world_info_sgc(?P<grow_condition>\d+)_sl(?P<seed_life>\d+)_spg(?P<prohibit_grow>.+?)_pl(?P<plant_life>\d+)_sm(?P<seed_mass>\d+)_pm(?P<plant_mass>\d+)_is(?P<init_soil>\d+)_fi(?P<dimension>\d+)\.csv'
	get = re.search(template, filename)
	r = None if get is None else get.groupdict()
	return r
	

def swap_filename(filename, img_dir):
	new_name = os.path.splitext(filename)[0] + '.jpg'
	new_name = os.path.split(new_name)[1]
	new_path =os.path.join(img_dir, new_name)
	return new_path

def draw_pic(filename, img_dir):

	graf_param_dict = parse_filename(filename)
	if graf_param_dict is not None:
		f = open(filename, 'r', encoding = 'UTF16')
		reader = csv.DictReader(f, delimiter='\t')
		time = []
		biomass = []
		seed_mass = []
		rot_mass = []
		soil = []
		for no, row in enumerate(reader):
			if no >1200:
				break
			time.append(no)
			biomass.append(float(row['biomass'].replace(',','.')))
			seed_mass.append(float(row['seed mass'].replace(',','.')))
			soil.append(float(row['soil'].replace(',','.')))
			rot_mass.append(float(row['rot mass'].replace(',','.')))
		plt.rc('xtick', labelsize=8)
		plt.rc('ytick', labelsize=8) 
		plt.rcParams.update({'font.size': 8})
		plt.figure(figsize=(8.5, 5))
		plt.subplot()

		labels = ('масса семян', 'биомасса', 'масса гнили','масса почвы')
		plt.stackplot(time, seed_mass, biomass, rot_mass, soil, labels=labels, colors = ( seed_color, plant_color, rot_color , soil_color), baseline='zero')

		fretil = biomass[0] + soil[0] - int(graf_param_dict["grow_condition"])*FIELDS_NUMBER_BY_SIDE*FIELDS_NUMBER_BY_SIDE

		plt.plot([time[0], time[-1]], [fretil, fretil], linewidth=1, color='#3333aa', alpha=.45, label='порог прорастания')
		
		tit = f'Масса почвы на клетке для прорастания семян: {int(graf_param_dict["grow_condition"])}.\n'
		tit += f'Срок запрета на прорастание: {int(float(graf_param_dict["prohibit_grow"])*24)}. '
		tit += f'Срок жизни семени: {int(float(graf_param_dict["seed_life"])*24)}. '
		tit += f'Масса семени: {int(graf_param_dict["seed_mass"])}. \n'
		tit += f'Срок жизни растения: {int(float(graf_param_dict["plant_life"])*24)}. '
		tit += f'Максмиатльная масса растения: {int(graf_param_dict["plant_mass"])}. '
		tit += f'Масса почвы на клетке: {int(graf_param_dict["init_soil"])}. '

		plt.title(tit)
		plt.xlabel('Время')
		plt.ylabel('Масса')
		plt.legend(loc='upper right')
		plt.grid(True, which='both',color='#dddddd', alpha=.45)
		plt.tight_layout()
		pic_name = swap_filename(filename, img_dir)
		plt.savefig(pic_name,  quality=100, optimize=True, format='jpg')
		plt.close()
