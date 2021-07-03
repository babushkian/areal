import sqlite3
import os
from areal import constants as cn

class WorldBase:

    def __init__(self, hvn, sim_dir):
        self.hvn = hvn
        base = os.path.join(sim_dir, 'world.db')
        self.conn = sqlite3.connect(base)
        self.c = self.conn.cursor()
        self.obj_type_associations = {'plant': {'new': self.insert_plant, 'obsolete':self.plant_death},
                                      'seed': {'new': self.insert_seed, 'obsolete': self.seed_death}
        }

        self.c.execute('PRAGMA foreign_keys=on')

        self.c.execute("""CREATE TABLE IF NOT EXISTS parameters (
            sim_id INTEGER PRIMARY KEY, 
            dimension INTEGER NOT NULL,
            sim_period INTEGER NOT NULL, 
            max_plants_on_field INTEGER NOT NULL, 
            init_soil INTEGER,
            grow_up_condition REAL, 
            seed_life REAL NOT NULL, 
            seed_prohibit_period REAL, 
            plant_life REAL NOT NULL, 
            fruiting_period REAL NOT NULL, 
            hidden_mass REAL, 
            seed_mass REAL NOT NULL, 
            max_plant_mass REAL NOT NULL,
            plant_number INTEGER,
            seeds_number INTEGER,
            rot_amount REAL,
            seeds_grow_up INTEGER,
            plant_mass_integral REAL, 
            soil_flow REAL
            )""")


        self.c.execute("""CREATE TABLE IF NOT EXISTS time (
            tick_id INTEGER PRIMARY KEY, 
            tick INTEGER, 
            sim_id INTEGER NOT NULL,
            FOREIGN KEY (sim_id) REFERENCES parameters (sim_id)
            )""")

        self.c.execute("""CREATE TABLE IF NOT EXISTS fields (
            field_id TEXT PRIMARY KEY,
            row INTEGER NOT NULL, 
            col INTEGER NOT NULL)""")

        self.c.execute("""CREATE TABLE IF NOT EXISTS plants (
            plant_id INTEGER PRIMARY KEY,
            field_id TEXT NOT NULL, 
            birth INTEGER, 
            death INTEGER DEFAULT NULL,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            FOREIGN KEY (field_id) REFERENCES fields (field_id),
            FOREIGN KEY (birth) REFERENCES time (tick_id)
            FOREIGN KEY (death) REFERENCES time (tick_id)
            )""")

        self.c.execute("""CREATE TABLE IF NOT EXISTS seeds (
            seed_id INTEGER PRIMARY KEY,
            field_id TEXT NOT NULL, 
            birth INTEGER, 
            death INTEGER DEFAULT NULL,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            FOREIGN KEY (field_id) REFERENCES fields (field_id),
            FOREIGN KEY (birth) REFERENCES time (tick_id)
            FOREIGN KEY (death) REFERENCES time (tick_id)
            )""")

        self.c.execute("""CREATE TABLE IF NOT EXISTS soil (
            id INTEGER PRIMARY KEY,
            field_id TEXT NOT NULL,
            tick_id INTEGER NOT NULL,
            soil REAL, 
            FOREIGN KEY (field_id) REFERENCES fields (field_id),
            FOREIGN KEY (tick_id) REFERENCES time (tick_id)
            )""")

        self.c.execute("""CREATE TABLE IF NOT EXISTS plant_mass (
            id INTEGER PRIMARY KEY,
            plant_id INTEGER NOT NULL,
            tick_id INTEGER NOT NULL,
            mass REAL, 
            all_energy REAL, 
            FOREIGN KEY (plant_id) REFERENCES plants (plant_id),
            FOREIGN KEY (tick_id) REFERENCES time (tick_id) 
            )""")

        self.c.execute("""CREATE TABLE IF NOT EXISTS rot_mass (
            id INTEGER PRIMARY KEY,
            field_id TEXT NOT NULL,
            tick_id INTEGER NOT NULL,
            rot_mass REAL, 
            FOREIGN KEY (field_id) REFERENCES fields (field_id),
            FOREIGN KEY (tick_id) REFERENCES time (tick_id)
            )""")

        self.conn.commit()

    def close_connection(self):
        self.conn.commit()
        self.c.close()
        self.conn.close()

    def db_write(self):
        '''
        Главная функция, которая записывает сосотяние поля в базу
        Добавляет новые объекты
        Добавляет для устаревших объектов дату смерти
        Обновляет сведения о массах растений и гнили
        '''
        self.insert_time()
        for pool in['new', 'obsolete']:
            for obj in self.hvn.world.change_scene[pool].values():
                func = self.obj_type_associations[obj.name][pool]
                func(obj)
        for field in self.hvn.world.fields.values():
            for obj in field.plants.values():
                self.update_plant_mass(obj)

    def insert_params(self):
        def param_tuple():
            t = [self.hvn.SIM_NUMBER]
            t.append(cn.FIELDS_NUMBER_BY_SIDE)
            t.append(cn.SIMULATION_PERIOD)
            t.append(cn.MAX_PLANTS_IN_FIELD)
            t.append(cn.INIT_SOIL)
            t.append(cn.SEED_GROW_UP_CONDITION)
            t.append(cn.SEED_LIFE)
            t.append(cn.SEED_PROHIBITED_GROW_UP)
            t.append(cn.PLANT_LIFETIME_YEARS)
            t.append(cn.FRUITING_PERIOD)
            t.append(cn.PLANT_HIDDEN_MASS)
            t.append(cn.SEED_MASS)
            t.append(cn.PLANT_MAX_MASS)
            return tuple(t)
        self.c.execute("""INSERT INTO parameters (sim_id,
                                            dimension, 
                                            sim_period, 
                                            max_plants_on_field, 
                                            init_soil, 
                                            grow_up_condition, 
                                            seed_life, 
                                            seed_prohibit_period, 
                                            plant_life, 
                                            fruiting_period, 
                                            hidden_mass, 
                                            seed_mass, 
                                            max_plant_mass) 
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (param_tuple()))

    def insert_metric(self, metric):
        self.c.execute("""UPDATE parameters  SET   
                                plant_number  = (?),
                                seeds_number  = (?),
                                rot_amount = (?), 
                                seeds_grow_up  = (?),
                                plant_mass_integral = (?),  
                                soil_flow = (?) 
                                WHERE sim_id = (?)""",  (*metric, self.hvn.SIM_NUMBER))

    def insert_time(self):
        self.tick_id = self.hvn.world.global_time + 1_000_000 * self.hvn.SIM_NUMBER
        self.c.execute('INSERT INTO time (tick_id, tick, sim_id) VALUES (?, ?, ?)',
                       (self.tick_id, self.hvn.world.global_time, self.hvn.SIM_NUMBER))

    def insert_field(self, field):
        self.c.execute('INSERT OR REPLACE INTO fields (field_id, row, col) VALUES (?, ?, ?)',
                       (field.id, field.row, field.col))

    def insert_plant(self, plant):
        self.c.execute('INSERT INTO plants (plant_id, field_id, birth, x, y) VALUES (?, ?, ?, ?, ?)',
                       (plant.id, plant.field.id, self.tick_id, plant.x, plant.y))

    def update_plant_mass(self, plant):
        self.c.execute('INSERT INTO  plant_mass (plant_id, tick_id, mass, all_energy) VALUES (?, ?, ?, ?)',
                       (plant.id, self.tick_id, plant.mass, plant.all_energy))

    def plant_death(self, plant):
        self.c.execute('UPDATE plants SET death = (?) WHERE plant_id = (?)', (self.tick_id, plant.id))


    def insert_seed(self, seed):
        self.c.execute('INSERT INTO seeds (seed_id, field_id, birth, x, y) VALUES (?, ?, ?, ?, ?)',
                       (seed.id, seed.field.id, self.tick_id, seed.x, seed.y))

    def seed_death(self, seed):
        self.c.execute('UPDATE seeds SET death = (?) WHERE seed_id = (?)', (self.tick_id, seed.id))

    def update_soil(self, field):
        self.c.execute('INSERT INTO  soil (field_id, tick_id, soil) VALUES (?, ?, ?)',
                       (field.id, self.tick_id, field.soil))

    def update_rot(self, field):
        self.c.execute('INSERT INTO  rot_mass (field_id, tick_id, rot_mass) VALUES (?, ?, ?)',
                       (field.id, self.tick_id, field.rot_mass))


    def commit(self):
        self.conn.commit()
