from flask import Flask, render_template
import subprocess
from markupsafe import escape

app = Flask(__name__)

@app.route('/flask_proj')
def hello_world():
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
