import mysql.connector

db_conn = mysql.connector.connect(host="kafka-nicholas.eastus2.cloudapp.azure.com", user="root", password="password", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
          CREATE TABLE member_checkin
          (id INT NOT NULL AUTO_INCREMENT,
           member_id VARCHAR(250) NOT NULL, 
           member_age VARCHAR(250) NOT NULL,
           member_name VARCHAR(250) NOT NULL,
           member_time_entered VARCHAR(100) NOT NULL,
           trace_id VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT membercheckin_pk PRIMARY KEY (id))
          ''')

db_cursor.execute('''
          CREATE TABLE gym_equipment
          (id INT NOT NULL AUTO_INCREMENT,
           machine_id VARCHAR(250) NOT NULL, 
           machine_name VARCHAR(250) NOT NULL,
           machine_time_used VARCHAR(100) NOT NULL,
           trace_id VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT gymequipmentinuse_pk PRIMARY KEY (id))
          ''')

db_conn.commit()
db_conn.close()
