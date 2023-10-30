import sqlite3, json
from sqlite3 import Error

 # Mods for folder store. Add folder to database, create items for N folders. Add folder to store calls

def create_connection(database):
    try:
        conn = sqlite3.connect(database, isolation_level=None, check_same_thread = False)
        conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        
        return conn
    except Error as e:
        print(e)

def create_table(c):
    sql = """ 
        CREATE TABLE IF NOT EXISTS items (
            i integer PRIMARY KEY,
            n varchar(225) NOT NULL,
            p varchar(225) NOT NULL,
            f varchar(225) NOT NULL,
            v integer NOT NULL Default 0
        ); 
    """
    c.execute(sql)
    sql = """
        CREATE TABLE IF NOT EXISTS meta (
            i integer PRIMARY KEY,
            k varchar(225) NOT NULL,
            v varchar(225) NOT NULL
        );
        """
    c.execute(sql)
    sql = """
        INSERT INTO meta(k,v) VALUES ('show','false');
    """
    c.execute(sql)
    sql = """
        INSERT INTO meta(k,v) VALUES ('folder', '2');
    """
    c.execute(sql)

def create_item(c, item):
    sql = ''' INSERT INTO items(n,p,f)
              VALUES (?,?,?) '''
    c.execute(sql, item)

def update_item_set(c, data):


    name = data['id']
    place = 4 - data['bid']
    member = data['member']
    f = get_photos_folder(c)
    print('update_item_set', (name, member, (4-place)))
    if name in "PYNR":
        mult = 0.5
    else:
        mult = 1

    if name != 'X':
        sql = ''' UPDATE items
                  SET v = 0
                  WHERE n = ? and v = ? and f = ?'''
        c.execute(sql, (name, place*mult,f))

    sql = ''' UPDATE items
              SET v = ?
              WHERE n = ? and p = ? and f = ?'''

    c.execute(sql, (place*mult, name, member, f))

def update_item_reset(c, item):
    f = get_photos_folder(c)
    sql = ''' UPDATE items
              SET v = 0
              WHERE n = ? and p = ? and f = ? '''
    c.execute(sql, (item, f))

def select_all_items(c):
    f = get_photos_folder(c)
    print(f)
    sql = ''' SELECT * FROM items where f = ? and not v = 0 '''
    c.execute(sql, f)
 
    rows = c.fetchall()
    return json.dumps(rows)


def toggle_show(c):
    sql = ''' SELECT * FROM meta where k="show" '''
    c.execute(sql)
    rows = c.fetchall()
    if rows[0]['v'] == 'true':
        sql = ''' UPDATE meta
                  SET v = "false"
                  WHERE k = "show"'''
        show = 'False'
    else:
        sql = ''' UPDATE meta
                  SET v = "true"
                  WHERE k = "show"'''
        show = 'True'
    c.execute(sql)
    return show


def get_show(c):
    sql = ''' SELECT * FROM meta where k="show" '''
    c.execute(sql)
    rows = c.fetchall()
    if rows[0]['v'] == 'true':
        show = 'True'
    else:
        show = 'False'
    return show


def get_photos_folder(c):
    sql = ''' SELECT * FROM meta where k="folder" '''
    c.execute(sql)
    rows = c.fetchall()
    return rows[0]['v']

def change_photos_folder(c, folder):
    sql = ''' UPDATE meta
              SET v = ?
              WHERE k = "folder"'''

    c.execute(sql, [folder+1])
    # sql = ''' UPDATE items
    #           SET v = 0'''
    # c.execute(sql)
    return folder


def db_reset_scores(c, folder):
    sql = ''' UPDATE items
              SET v = 0 where f = ?'''
    c.execute(sql, folder)
    return

def main():
    database = "./pythonsqlite.db"

    # create a database connection
    conn = create_connection(database)

    # create items table
    create_table(conn)
    for folder in range(10):
        for name in 'CMVTAPYNRX':
            for photo in range(24):
                create_item(conn, (name,photo,folder))
    print("Connection established!")

if __name__ == '__main__':
    main()



