import psycopg2
import os
import json
from dbconfig import hostname, username, password, database

photos_root = "/var/www/python-realtime-poll-pusher/static/photos"


 # Mods for folder store. Add folder to database, create items for N folders. Add folder to store calls

def create_connection():
    try:
        #conn = sqlite3.connect(database, isolation_level=None, check_same_thread = False)
        #conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        conn.autocommit = True
        return conn
    except Error as e:
        print(e)

def create_table(c):
    cur = c.cursor()
    sql = "DROP TABLE META"
    cur.execute(sql)
    sql = "DROP TABLE ITEMS"
    cur.execute(sql)
    sql = """
        CREATE TABLE items (
          
            n varchar(225) NOT NULL,
            p varchar(225) NOT NULL,
            f varchar(225) NOT NULL,
            v integer NOT NULL Default 0
        ); 
    """
    cur.execute(sql)
    sql = """
        CREATE TABLE IF NOT EXISTS meta (
     
            k varchar(225) NOT NULL,
            v varchar(225) NOT NULL
        );
        """
    cur.execute(sql)
    sql = """
        INSERT INTO meta(k,v) VALUES ('show','false');
    """
    cur.execute(sql)
    sql = """
        INSERT INTO meta(k,v) VALUES ('folder', 'a');
    """
    cur.execute(sql)

def create_item(c, item):

    cur = c.cursor()

    sql = ''' INSERT INTO items(n,p,f)
              VALUES (%s,%s,%s) '''
    cur.execute(sql, item)

def update_item_set(c, data):
    cur = c.cursor()

    name = data['id']
    place = 4 - data['bid']
    member = data['member']
    f = get_photos_folder(c)
    if name in "PYNR":
        mult = 1
    else:
        mult = 2

    sql = '''SELECT v FROM items WHERE v = %s and  n = %s and p = %s and f = %s'''
    cur.execute(sql, (place*mult, name, member, f))
    rows = cur.fetchall()

    if len(rows) != 0:
        found_item = True
    else:
        found_item = False

    if name != 'X':

        sql = ''' UPDATE items
                  SET v = 0
                  WHERE n = %s and v = %s and f = %s'''
        cur.execute(sql, (name, place*mult,f))

    if not found_item:
        sql = ''' UPDATE items
                  SET v = %s
                  WHERE n = %s and p = %s and f = %s'''

        cur.execute(sql, (place*mult, name, member, f))

def update_item_reset(c, item):
    cur = c.cursor()
    f = get_photos_folder(c)
    sql = ''' UPDATE items
              SET v = 0
              WHERE n = %s and p = %s and f = %s '''
    cur.execute(sql, (item, f))

def select_all_items(c):
    cur = c.cursor()
    f = get_photos_folder(c)
    sql = ''' SELECT * FROM items where f = %s and not v = 0 '''
    cur.execute(sql, (f,))
 
    rows = cur.fetchall()
    out = []
    for row in rows:
        out.append( {'n':row[0], 'p':row[1], 'f':row[2], 'v':row[3]} )
    return json.dumps(out)


def toggle_show(c):
    cur = c.cursor()
    sql = """ SELECT * FROM meta where k='show' """
    cur.execute(sql)
    rows = cur.fetchall()
    if rows[0][1] == 'true':
        sql = """ UPDATE meta
                  SET v = 'false'
                  WHERE k = 'show'"""
        show = 'False'
    else:
        sql = """ UPDATE meta
                  SET v = 'true'
                  WHERE k = 'show'"""
        show = 'True'
    cur.execute(sql)
    return show


def get_show(c):
    cur = c.cursor()
    sql = """ SELECT * FROM meta where k='show' """
    cur.execute(sql)
    rows = cur.fetchall()
    if rows[0][1] == 'true':
        show = 'True'
    else:
        show = 'False'
    return show


def get_photos_folder(c):
    cur = c.cursor()
    sql = """ SELECT * FROM meta where k='folder' """
    cur.execute(sql)
    rows = cur.fetchall()
    return rows[0][1]

def change_photos_folder(c, folder):
    cur = c.cursor()
    sql = """ UPDATE meta
              SET v = %s
              WHERE k = 'folder'"""

    cur.execute(sql, (folder,))
    # sql = ''' UPDATE items
    #           SET v = 0'''
    # c.execute(sql)
    return folder


def db_reset_scores(c, folder):
    cur = c.cursor()
    sql = """ UPDATE items
              SET v = 0 where f = %s AND n != 'X'"""
    cur.execute(sql, (folder,))
    return

def main():

    # create a database connection
    conn = create_connection()

    # create items table
    create_table(conn)
    dirs = os.listdir(photos_root)
    sdirs = sorted(dirs)
    for folder in sdirs:
        for name in 'LMVFBPYNRX':
            for photo in range(24):
                create_item(conn, (name,photo,folder))
    print("Connection established!")

if __name__ == '__main__':
    main()



