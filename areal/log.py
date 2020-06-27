import os
from areal import constants as cn
from areal.plant import Plant
from areal.seed import Seed
from areal.rot import Rot
class Log:
    def __init__(self, parent):
        self.parent = parent
        self.world = parent.world
        self.logfile_associations = {'every_plant_life': self.log_plants,
                             'fields_info': self.log_fields,
                             'world_info': self.log_world}
        self.log_functions = {} # словарь содержит функции, которые должны вызываться для логирования ключевого файла
        suffix = self.file_suffix()
        for action, name, header in cn.LOGGING:
            if action:
                fname = os.path.join(self.parent.sim_dir, f'{name}_{suffix}.csv')
                f = open(fname, 'w', encoding='UTF16')
                f.write(header)
                self.log_functions[f] = self.logfile_associations[name]


    def log_world(self, file):
        s = f'{self.world.years}\t{self.world.global_time}\t{Plant.COUNT}\t'
        s += f'{Plant.COUNT - self.parent.starving}\t{self.parent.starving}\t'
        s += f'{Seed.COUNT}\t'
        s += f'{Rot.COUNT}\t'
        s += f'{self.parent.seed_mass:8.1f}\t{self.parent.plant_mass:8.1f}\t{self.parent.rot_mass:8.1f}\t'
        s += f'{self.parent.soil_mass:8.1f}\t{self.parent.world_mass:8.1f}\n'
        file.write(s.replace('.', ','))

    def log_fields(self, file):
        for row in range(cn.FIELDS_NUMBER_BY_SIDE):
            for col in range(cn.FIELDS_NUMBER_BY_SIDE):
                file.write(self.world.fields[row][col].write_info())

    def log_plants(self, file):
        for row in range(cn.FIELDS_NUMBER_BY_SIDE):
            for col in range(cn.FIELDS_NUMBER_BY_SIDE):
                for plant in self.world.fields[row][col].plants.values():
                    file.write(plant.info())

    @staticmethod
    def file_suffix():
        suffix = list()
        suffix.append(f'sgc{cn.SEED_GROW_UP_CONDITION:03}')
        suffix.append(f'sl{cn.SEED_LIFE:03}')
        suffix.append(f'spg{cn.SEED_PROHIBITED_GROW_UP:03}')
        suffix.append(f'pl{cn.PLANT_LIFETIME_YEARS:03}')
        suffix.append(f'sm{cn.SEED_MASS:03}')
        suffix.append(f'pm{cn.PLANT_MAX_MASS:03}')
        suffix.append(f'is{cn.INIT_SOIL:03}')
        suffix.append(f'fi{cn.FIELDS_NUMBER_BY_SIDE:03}')
        s = '_'.join(suffix)
        return s

    def write(self):
        for file in self.log_functions:
            self.log_functions[file](file)

    def logging_close(self):
        for file in self.log_functions:
            if not file.closed:
                file.close()

    @staticmethod
    def population_metric_head(file):
        s = 'dimension\t'
        s += 'end date\t'
        s += 'soil on tile\t'
        s += 'grow up condition\t'
        s += 'prohibited grow up period\t'
        s += 'seed life\t'
        s += 'seed mass\t'
        s += 'plant life\t'
        s += 'plant mass\t'
        s += 'plants number\t'
        s += 'seeds number\t'
        s += 'grow up seeds percent\t'
        s += 'total plant enetgy\t'
        s += 'total soil flow\n'
        file.write(s)

    def population_metric_record(self, file):
        s = list()
        s.append(str(cn.FIELDS_NUMBER_BY_SIDE))
        s.append(str(self.world.global_time))
        s.append(str(cn.INIT_SOIL))
        s.append(str(cn.SEED_GROW_UP_CONDITION))
        s.append(str(cn.SEED_PROHIBITED_GROW_UP))
        s.append(str(cn.SEED_LIFE))
        s.append(str(cn.SEED_MASS))
        s.append(str(cn.PLANT_LIFETIME_YEARS))
        s.append(str(cn.PLANT_MAX_MASS))
        #s.append(str(self.parent.sign_plant_num))
        #s.append(str(self.sign_seeds_born))
        #s.append(f'{(self.sign_seeds_grow_up /self.sign_seeds_born *100 if self.sign_seeds_born > 0 else 0 ):4.1f}')
        #s.append(f'{self.sign_plant_mass_energy:10.0f}')
        #s.append(f'{self.soil_flow:10.0f}')
        s.append('\n')
        string = '\t'.join(s)
        string=string.replace('.', ',')
        file.write(string)

