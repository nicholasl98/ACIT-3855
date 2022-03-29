import sqlite3

conn = sqlite3.connect('stats.sqlite')

c = conn.cursor()
c.execute(''' 
          CREATE TABLE stats
          (id INTEGER PRIMARY KEY ASC,
           num_membercheckin_readings INTEGER NOT NULL, 
           max_member_age_reading VARCHAR(250),
           max_machine_name_reading VARCHAR(250),
           num_gymequipmentuse_readings INTEGER NOT NULL,
           last_updated VARCHAR(100) NOT NULL)
          ''')

conn.commit()
conn.close()