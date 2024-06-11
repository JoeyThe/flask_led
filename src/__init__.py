from flask import Flask, render_template, request, flash
import subprocess
from markupsafe import escape
import sqlite3
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tangeloines'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/flask_proj', methods=('GET', 'POST'))
def hello_world():
    if request.method == 'POST':
        bird_id = request.form['bird_id']
        region_id = request.form['region_id']
        optional_days_back = request.form['optional_days_back']
        optional_max_results = request.form['optional_max_results']
        # Check to make sure we got the required fields
        if bird_id == "" or region_id == "":
            print("Bird ID and Region ID must be supplied")
            # Code to generate/return an index page with warning text
            # Can these checks also be done by JS?
        # Check to make sure optional parameters are integers
        try:
            if optional_days_back != "":
                optional_days_back_int = int(optional_days_back)
            if optional_max_results != "":
                optional_max_results_int = int(optional_max_results)
        except Exception as e:
            print("Days Back and Max Results must be integers")
        bird_get_resp = getSpeciesInfoForRegion(region_id,bird_id,optional_days_back,optional_max_results)
        bird_data = {
            "Common Name"       : bird_get_resp[0]['comName'],
            "Scientific Name"   : bird_get_resp[0]['sciName'],
            "Date Observed"     : bird_get_resp[0]['obsDt'],   
            "Location Observed" : bird_get_resp[0]['locName'],
            "Number Observed"   : str(bird_get_resp[0]['howMany'])
        }
        bird_data_txt = "\n".join([field+" = "+bird_data[field] for field in bird_data])
        return render_template('index.html', bird_get_resp=bird_data_txt)
        
            # Code to generate/return an index page with warning text
            # Can these checks also be done by JS?
        # if not title:
        #     flash('Title is required!')
        # elif not content:
        #     flash('Content is required!')
        # else:
        #     conn = get_db_connection()
        #     conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
        #                 (title, content))
        #     conn.commit()
        #     posts = conn.execute('SELECT * FROM posts').fetchall()
        #     for post in posts:
        #         print(str(post['id'])+", "+post['title']+", "+post['content'])
        #     conn.close()
    return render_template('index.html')

@app.get('/service_status/<service>')
def populate_mc_info(service):
    # Run subprocess for getting service status
    try:
        sub = subprocess.run(['systemctl','status',escape(service)], check=False, stdout=subprocess.PIPE)
        output = sub.stdout.decode()
        # output = output.replace('\n','<br>')
        return output
    except Exception as e:
        app.logger.ERROR(e)
        return "Error"

# Non-app funcitons
def getSpeciesInfoForRegion(regionCode, speciesCode, back=30, maxResults=1):
    back = 30
    maxResults = 1
    params = {
        'back': back,
        'maxResults': maxResults
    }
    headers = {'X-eBirdApiToken': '2fkoo1rimpng'}
    url = f'https://api.ebird.org/v2/data/obs/{regionCode}/recent/{speciesCode}'
    r = requests.get(url, headers=headers, params=params)
    data = r.json()
    print(data)
    return data
