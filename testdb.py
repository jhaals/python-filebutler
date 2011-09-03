import sqlite3

conn = sqlite3.connect('/Users/jhaals/db.database')

c = conn.cursor()

c.execute('''create table files
(hash text, user_id int, filename text, expire text, one_time_download bool)''')

c.execute('''create table users
(user_id int, username text, password text)''')
c.execute("""insert into users (user_id, username, password) values ('1', 'louie', '123')""")

conn.commit()
#c.execute("select user_id from users where username='louie' and password='123'")
#r = c.fetchone()
c.close()
