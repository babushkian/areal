import sqlite3
import os

class WorldBase:

    def __init__(self, world, dir):
        self.world = world
        base = os.path.join(dir, 'world.db')
        self.conn = sqlite3.connect(base)
        self.c = self.conn.cursor()
        '''
        self.c.execute('DROP TABLE IF EXISTS parameters')
        self.c.execute('DROP TABLE IF EXISTS time')
        self.c.execute('DROP TABLE IF EXISTS fields')
        self.c.execute('DROP TABLE IF EXISTS soil')
        self.c.execute('DROP TABLE IF EXISTS plants')
        self.c.execute('DROP TABLE IF EXISTS plant_mass')
        '''
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
            max_plant_mass REAL NOT NULL)""")

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
            sim_id INTEGER NOT NULL,
            FOREIGN KEY (field_id) REFERENCES fields (field_id),
            FOREIGN KEY (sim_id) REFERENCES parameters (sim_id)
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

        self.conn.commit()

    def close_coonection(self):
        self.conn.commit()
        self.c.close()
        self.conn.close()


    def insert_params(self, params):
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
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (params))


    def insert_time(self):
        self.tick_id = self.world.global_time + 1_000_000 * self.world.sim_number
        self.c.execute('INSERT INTO time (tick_id, tick, sim_id) VALUES (?, ?, ?)',
                       (self.tick_id, self.world.global_time, self.world.sim_number))

    def insert_field(self, field):
        self.c.execute('INSERT OR REPLACE INTO fields (field_id, row, col) VALUES (?, ?, ?)', (field.id, field.row, field.col))

    def insert_plant(self, plant):
        self.c.execute('INSERT INTO plants (plant_id, field_id, sim_id) VALUES (?, ?, ?)',
                       (plant.id, plant.field.id, self.world.sim_number))

    def update_soil(self, field):
        self.c.execute('INSERT INTO  soil (field_id, tick_id, soil) VALUES (?, ?, ?)', (field.id, self.tick_id, field.soil))

    def update_plant_mass(self, plant):
        self.c.execute("""INSERT INTO  plant_mass (plant_id, tick_id, mass, all_energy) VALUES (?, ?, ?, ?)""",
                       (plant.id, self.tick_id, plant.mass, plant.all_energy))


    def commit(self):
        self.conn.commit()
