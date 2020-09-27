import sqlite3
import time
import sys
import os

if len(sys.argv)<2:
	print("Не Не указана папка, подержащая базу.")
	sys.exit(1)



base_file = os.path.join(sys.argv[1], 'world.db')
targ_file = "world_report.csv"

if not os.path.exists(base_file):
	print('Не найдена база.')
	sys.exit(2)

conn = sqlite3.connect(base_file)
c = conn.cursor()

t1 = time.time()

c.execute('CREATE INDEX IF NOT EXISTS plant_mass_idx  ON plant_mass (plant_id)')
c.execute('CREATE INDEX IF NOT EXISTS plant_tick_idx  ON plant_mass (tick_id)')
c.execute('CREATE INDEX IF NOT EXISTS soil_tick_idx  ON soil (tick_id)')
c.execute('CREATE INDEX IF NOT EXISTS seed_birth_idx  ON seeds (birth)')
c.execute('CREATE INDEX IF NOT EXISTS seed_death_idx  ON seeds (death)')

t2 = time.time()
c.execute('''SELECT tick_id
		FROM time
		WHERE sim_id = 1
		ORDER BY tick_id''')
x = c.fetchall()

t3 = time.time()
for i in x:
	c.execute('''SELECT SUM(soil)
		FROM soil
		WHERE tick_id = (?)''', i)
	field_soil = c.fetchall()
	c.execute('''SELECT SUM(all_energy)
		FROM plant_mass
		WHERE tick_id = (?)''', i)
	plant_mass = c.fetchall()
	c.execute('''SELECT SUM(mass)
		FROM rot_mass
		WHERE tick_id = (?)''', i)
	rot_mass = c.fetchall()

	'''
	SELECT SUM(soil.soil), SUM(plant_mass.all_energy), SUM(rot_mass.mass) 
	FROM FROM soil 
	INNER JOIN plant_mass
		ON soil.tick_id = plant_mass.tick_id
	INNER JOIN rot_mass
		ON soil.tick_id = rot_mass.tick_id
	WHERE soil.tick_id = (?)
			
	'''

	"""
	c.execute('''SELECT 5*COUNT(seed_id)
		FROM seeds
		WHERE birth <= (?)
			AND death >= (?)''', (i[0], i[0]))
	seed_mass = c.fetchall()
	"""

	print(field_soil, plant_mass, rot_mass, seed_mass)
"""
	# без нужного индекса очень медленно работает
	c.execute('''SELECT plant_mass.plant_id, plants.field_id,plant_mass.mass 
			FROM plant_mass INNER JOIN plants
			ON plant_mass.plant_id = plants.plant_id
			WHERE tick_id = (?)''', i)
	plants = c.fetchall()
	#print(plants)
"""
t4 = time.time()

conn.close()
print('index time: ', t2 - t1)
print('query time: ', t3 - t2)
print('cycle time: ', t4 - t3)
