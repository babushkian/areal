import sqlite3


conn = sqlite3.connect('world.db')
c = conn.cursor()
c.execute('''SELECT  plant_id, tick, mass 
		FROM plant_mass, fields 
		WHERE fields.field_id = "05x05" AND plant_id > 500 AND tick < 500 
		ORDER BY plant_id''')
p = c.fetchall()
conn.close()
for x in p:
	print(x)
	


