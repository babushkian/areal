import csv
from abc import ABC
from pathlib import Path
from areal import constants as cn
from areal.plant import Plant
from areal.seed import Seed



plant_header = ['time', 'ID', 'plant coords', 'age', 'mass', 'total food consumed', 'food to live',
               'food to grow', 'food ability', 'get food', 'mass delta', 'soil in field']

field_header = ['global time', 'coordinates', 'plants', 'seeds', 'biomass', 'rot mass', 'seeds mass',
                'soil', 'total mass']
world_header = ['year', 'glob time', 'total plants', 'full', 'starving', 'seeds', 'seed mass',
                'biomass', 'rot mass', 'soil', 'total mass']

LOGGING = ((cn.WRITE_PLANTS_INFO, 'every_plant_life', plant_header),
           (cn.WRITE_FIELDS_INFO, 'fields_info', field_header),
           (cn.WRITE_WORLD_INFO, 'world_info', world_header))

class Log:
    def __init__(self, hvn, sim_dir):
        self.hvn = hvn
        '''
        self.logfile_associations = {'every_plant_life': self.log_plants,
                             'fields_info': self.log_fields,
                             'world_info': self.log_world}
        '''
        self.logfile_associations = {'every_plant_life': PlantLogger,
                             'fields_info': FieldLogger,
                             'world_info': WorldLogger}
        self.logger = dict() # словарь содержит классы, которые должны вызываться для логирования ключевого файла
        suffix = self.file_suffix()
        for action, filename, header in LOGGING:
            if action:
                fname = Path(sim_dir, f'{filename}_{suffix}.csv')
                log_object = self.logfile_associations[filename](self.hvn, fname, header)
                self.logger[filename] = log_object


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
        for writer in self.logger.values():
            writer.write()

    def logging_close(self):
        for writer in self.logger.values():
                writer.close()

    def population_metric_record(self, file):
        s = list()
        s.append(str(cn.FIELDS_NUMBER_BY_SIDE))
        s.append(str(self.hvn.world.global_time))
        s.append(str(cn.INIT_SOIL))
        s.append(str(cn.SEED_GROW_UP_CONDITION))
        s.append(str(cn.SEED_PROHIBITED_GROW_UP))
        s.append(str(cn.SEED_LIFE))
        s.append(str(cn.SEED_MASS))
        s.append(str(cn.PLANT_LIFETIME_YEARS))
        s.append(str(cn.PLANT_MAX_MASS))
        s.append(str(self.hvn.sign_plant_num))
        s.append(str(self.hvn.sign_seeds_born))
        s.append(f'{self.hvn.sign_rot_amount:10.1f}')
        s.append(f'{(self.hvn.sign_seeds_grow_up /self.hvn.sign_seeds_born *100 if self.hvn.sign_seeds_born > 0 else 0 ):4.1f}')
        s.append(f'{self.hvn.sign_plant_mass_integral:10.1f}')
        s.append(f'{self.hvn.soil_flow:10.1f}')
        s.append('\n')
        string = '\t'.join(s)
        string = string.replace('.', ',')
        file.write(string)

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
    s += 'rot amount\t'
    s += 'grow up seeds percent\t'
    s += 'integral_plant_mass\t'
    s += 'total soil flow\n'
    file.write(s)


class Logger(ABC):
    def __init__(self, hvn, filename, header):
        self.hvn = hvn
        self.file = open(filename, 'w', encoding='utf16')
        self.writer=csv.DictWriter(self.file, header, dialect=csv.unix_dialect)
        self.writer.writeheader()
        self.dict_defined = False

    def close(self):
        if not self.file.closed:
            self.file.close()


class PlantLogger(Logger):
    def write(self):
        row = dict()
        for field in self.hvn.world.fields.values():
            for plant in field.plants.values():
                self.writer.writerow(plant.info_dict())
        self.writer.writerow(row)


class FieldLogger(Logger):
    def write(self):
        for field in self.hvn.world.fields.values():
            self.writer.writerow(field.info_dict())


class WorldLogger(Logger):
    def write(self):
        s = dict()
        s['year'] = f'{self.hvn.world.years}'
        s['glob time'] = f'{self.hvn.world.global_time}'
        s['total plants'] = f'{Plant.COUNT}'
        s['full'] = f'{Plant.COUNT - self.hvn.starving}'
        s['starving'] = f'{self.hvn.starving}'
        s['seeds'] = f'{Seed.COUNT}'
        s['seed mass'] = f'{self.hvn.seed_mass:8.1f}'.replace('.', ',')
        s['biomass'] = f'{self.hvn.plant_mass:8.1f}'.replace('.', ',')
        s['rot mass'] = f'{self.hvn.rot_mass:8.1f}'.replace('.', ',')
        s['soil'] = f'{self.hvn.soil_mass:8.1f}'.replace('.', ',')
        s[ 'total mass'] = f'{self.hvn.world_mass:8.1f}'.replace('.', ',')
        self.writer.writerow(s)

