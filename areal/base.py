import sqlite3
import os

class WorldBase:

    def __init__(self, dir):
        base = os.path.join(dir, 'world.db')
        self.conn = sqlite3.connect(base)
        self.c = self.conn.cursor()

        self.c.execute('DROP TABLE IF EXISTS parameters')
        self.c.execute('DROP TABLE IF EXISTS time')
        self.c.execute('DROP TABLE IF EXISTS fields')
        self.c.execute('DROP TABLE IF EXISTS soil')
        self.c.execute('DROP TABLE IF EXISTS plants')
        self.c.execute('DROP TABLE IF EXISTS plant_mass')


        self.c.execute("""CREATE TABLE IF NOT EXISTS parameters (
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

        self.c.execute('CREATE TABLE IF NOT EXISTS time (tick INTEGER PRIMARY KEY)')

        self.c.execute("""CREATE TABLE IF NOT EXISTS fields (
            field_id TEXT PRIMARY KEY,
            x INTEGER NOT NULL, 
            y INTEGER NOT NULL)""")

        self.c.execute("""CREATE TABLE IF NOT EXISTS plants (
            plant_id INTEGER PRIMARY KEY,
            field_id TEXT NOT NULL)""")

        self.c.execute("""CREATE TABLE IF NOT EXISTS soil (
            id INTEGER PRIMARY KEY,
            field_id TEXT NOT NULL,
            tick INTEGER NOT NULL,
            soil REAL)""")

        self.c.execute("""CREATE TABLE IF NOT EXISTS plant_mass (
            id INTEGER PRIMARY KEY,
            plant_id INTEGER NOT NULL,
            tick INTEGER NOT NULL,
            mass REAL, 
            all_energy REAL)""")

        self.conn.commit()

    def close_coonection(self):
        self.conn.commit()
        self.c.close()
        self.conn.close()


    def insert_params(self, params):
        self.c.execute("""INSERT INTO parameters (dimension, 
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
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (params))


    def insert_time(self,time):
        self.c.execute('INSERT INTO time (tick) VALUES (?)', (time,))

    def insert_field(self, f, x, y):
        self.c.execute('INSERT INTO fields (field_id, x, y) VALUES (?, ?, ?)', (f, x, y))

    def insert_plant(self, id, field_id):
        self.c.execute('INSERT INTO plants (plant_id, field_id) VALUES (?, ?)', (id, field_id))

    def update_soil(self, field_id, time, soil):
        self.c.execute('INSERT INTO  soil (field_id, tick, soil) VALUES (?, ?, ?)', (field_id, time, soil))

    def update_plant_mass(self, plant_id, time, mass, all_energy):
        self.c.execute("""INSERT INTO  plant_mass (plant_id, tick, mass, all_energy) VALUES (?, ?, ?, ?)""",
                       (plant_id, time, mass, all_energy))


    def commit(self):
        self.conn.commit()
"""
fff = load_family_names()
for fm in fff:
	c.execute('INSERT INTO family (fem, male) VALUES(?, ?)', (fm))

fff = load_fem_names()
for fm in fff:
	c.execute('INSERT INTO fem_names (first_name) VALUES("{}")'.format(fm))

fff = load_male_names()
for fm in fff:
	c.execute('INSERT INTO male_names (first_name, second_name_fem, second_name_male) VALUES(?, ?, ?)', (fm))

conn.commit()
c.close()
conn.close()
"""