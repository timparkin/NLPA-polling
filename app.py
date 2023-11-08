from flask import Flask, render_template, request, jsonify, make_response
from dbsetup import create_connection, select_all_items, update_item_set, update_item_reset, toggle_show, get_show, get_photos_folder, change_photos_folder, db_reset_scores
from flask_cors import CORS, cross_origin
from pusher import Pusher
import simplejson, json
import os, pickle
import psycopg2

from pusher_config_master import app_id, key as app_key, secret as app_secret, cluster
from dbconfig import hostname, username, password, database

photos_root = "/var/www/python-realtime-poll-pusher/static/photos"

name_lookup = {
    'C': 'Charlotte Gibb',
    'M': 'Michael Shainblum',
    'V': 'Victoria Haack',
    'T': 'Theo Bosboom',
    'A': 'Andy Mumford',
    'P': 'Tim Parkin',
    'Y': 'Matt Payne',
    'N': 'Alex Nail',
    'R': 'Rajesh Jyothiswaran',
    'X': 'show-hide',

}
vote_types = {
    'C': 'j',
    'M': 'j',
    'V': 'j',
    'T': 'j',
    'A': 'j',
    'P': 'o',
    'Y': 'o',
    'N': 'o',
    'R': 'o',
    'X': 'o',
}


photos_folder = "/var/www/python-realtime-poll-pusher/static/photos/1"

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.debug=True
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
pusher = Pusher(app_id=app_id, key=app_key, secret=app_secret, cluster=u'eu')

def create_connection():
    try:
        #conn = sqlite3.connect(database, isolation_level=None, check_same_thread = False)
        #conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        conn.autocommit = True
        return conn
    except Error as e:
        print(e)


c = create_connection()

element_html = """
            <div class="box poll-member" id="{id}" pindex="{pindex}">
              
                <h3>{element_name}</h3>
                <img class="img-thumbnail" src="/static/photos/{photos_folder}/{photo}" width="100%" />
                <div class="buttons"><span class="button button1 {selected1}">①</span><span class="button button2 {selected2}">②</span><span class="button button3 {selected3}">③</span><span class="button button4 {selected4}">④</span></div>
                <div class="percentageBarParent">
                <div class="percentageBar"></div>
                <div class="percentage"><span style="float:right" class="score"></span> <span style="text=align:left" class="percent"></span></div>
              </div>
              
            </div>
"""



def main():
    global conn, c

@app.route('/home/<id>')
def index(id):
    html = ''

    if id in "PYNR":
        mult = 1 
    else:
        mult = 2
    vote_type = vote_types[id]

    photos_folder = get_photos_folder(c)
    photos_path = os.path.join(photos_root,photos_folder)
    photos = os.listdir(photos_path)
    photos.sort()
    num_elements = len(photos)
    output = select_all_items(c)
    photo1 = None
    photo2 = None
    photo3 = None
    photo4 = None
    for r in json.loads(output):
        if r['n'] == id and r['v'] == 1*mult:
            photo4 = r['p']
        if r['n'] == id and r['v'] == 2*mult:
            photo3 = r['p']
        if r['n'] == id and r['v'] == 3*mult:
            photo2 = r['p']
        if r['n'] == id and r['v'] == 4*mult:
            photo1 = r['p']


    name = name_lookup[id]
    admin_html = ""
    if id in 'PYNR':
        admin_html = "<div>folder: "
        admin_html_template = """
            <span class="folder f{i} {selected}">{i}</span>
        """
        for i in range(24):
            if os.path.isdir(os.path.join(photos_root,str(i+1))):
                if photos_folder == str(i+1):
                    admin_html += admin_html_template.format(i=i+1, selected='selected')
                else:
                    admin_html += admin_html_template.format(i=i+1, selected='')

        admin_html += "</div><div>"
        admin_html += """
        <a onclick="tinysort('.wrapper .poll-member',{order:'desc',selector:'.score'})">sort by score</a> /
    <a onclick="tinysort('.wrapper .poll-member',{selector:'h3'})">sort reset</a> /
    <a onclick="reset_scores()">set scores to zero</a> /
    <span class="toggleshow"><span class="showing">hide results from judges</span><span class="hiding">show results to judges</span></span></div>
    """

    for i in range(num_elements):
        if photo1 and i == int(photo1):
            selected1 = 'selected'
        else:
            selected1 = ''
        if photo2 and i == int(photo2):
            selected2 = 'selected'
        else:
            selected2 = ''
        if photo3 and i == int(photo3):
            selected3 = 'selected'
        else:
            selected3 = ''
        if photo4 and i == int(photo4):
            selected4 = 'selected'
        else:
            selected4 = ''
        html += element_html.format( pindex=i, element_name=i+1,id=id,photo=photos[i],photos_folder=photos_folder,selected1=selected1,selected2=selected2,selected3=selected3,selected4=selected4)
    return render_template('index.html', html=html, vote_type=vote_type,admin_html=admin_html, name=name, photos_folder = photos_folder)

@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/vote', methods=['GET', 'POST'])  # /landingpageA
def vote():

    # load request data
    data = simplejson.loads(request.data)
    # update database with data for member
    update_item_set(c, data)
    # get all data back from db
    output = select_all_items(c)
    # fire an update with all of this data
    pusher.trigger(u'poll', u'vote', output)
    # return request
    return request.data


@app.route('/hide', methods=['GET', 'POST'])
def hide():

    # load request data

    data = simplejson.loads(request.data)
    if data['hide'] == 'hide':
        data['bid'] = 0
    else:
        data['bid'] = 2

    update_item_set(c, data)
    # fire an update with all of this data
    pusher.trigger(u'poll', u'hide', json.dumps(data))

    # return request
    return request.data

@app.route('/load', methods=['GET', 'POST'])
def load():
    # get all data back from db
    output = select_all_items(c)
    pusher.trigger(u'poll', u'vote', output)
    return request.data

@app.route('/toggleshow', methods=['GET', 'POST'])
def toggleshow():
    # get all data back from db
    output = toggle_show(c)
    pusher.trigger(u'poll', u'toggleshow', output)
    return output

@app.route('/getshow', methods=['GET', 'POST'])
def getshow():
    # get all data back from db
    output = get_show(c)
    pusher.trigger(u'poll', u'toggleshow', output)
    return output

@app.route('/change_folder', methods=['GET', 'POST'])
def change_folder():
    # get all data back from db
    data = simplejson.loads(request.data)
    folder = data['index']
    change_photos_folder(c, folder)
    output = select_all_items(c)
    pusher.trigger(u'poll', u'refresh', output)
    return output

@app.route('/reset_scores', methods=['GET', 'POST'])
def reset_scores():
    # get all data back from db
    photos_folder = get_photos_folder(c)
    db_reset_scores(c, photos_folder)
    output = select_all_items(c)
    pusher.trigger(u'poll', u'refresh', output)
    return output



if __name__ == '__main__':
    main()
    app.run(debug=True)
