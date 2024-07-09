from flask import Flask,request,jsonify,render_template,flash,abort
import psycopg2
from psycopg2 import extras
from datetime import datetime as dt
import glob
import random
import string
import json

app = Flask(__name__)
conn = psycopg2.connect('') # Setup Your PostgreSQL Database Setting

upfolder = './static/standby/'

@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/upload_form')
def upload_form():

    standbylist = glob.glob(upfolder + '*')

    print(standbylist)

    if len(standbylist) > 0:

        return render_template('standby.html')
    else:
        return render_template('upload_form.html')

@app.route('/img-upload',methods=['POST'])
def img_upload():

    if request.method == 'POST':

        imgfile = request.files['cropped-img']
        current = dt.now()
        current = current.strftime('%Y%m%d-%H%M%S')
        ext = imgfile.filename.split('.')[-1]
        filename = current + '.' + ext
        filepath = upfolder + filename
        imgfile.save(filepath)

        return render_template('uploaded.html',filepath=filepath)
    
@app.route('/form_device_reg',methods=['GET','POST'])
def form_device_register():
    cur = conn.cursor()
    sql = "SELECT * FROM devices;"
    cur.execute(sql)
    res = cur.fetchall()
    conn.commit()
    cur.close()
    title = 'Device Registration'
    return render_template('device_regform.html',title=title,res=res)

@app.route('/current',methods=['GET','POST'])
def current():

    return render_template('current.html')

@app.route('/ranking',methods=['GET','POST'])
def ranking():

    cur = conn.cursor()
    sql = "select archive,artid,serial_num,filename,sum(duration),count(session_facecount_id) from facecount_log group by archive,artid,serial_num,filename order by sum desc;"
    cur.execute(sql)
    res = cur.fetchall()
    conn.commit()
    cur.close()

    return render_template('ranking.html',res=res)

@app.route('/device-register',methods=['POST'])

def device_register():

    if request.method == 'POST':
        device_name = request.form['device_name']
        description = request.form['description']
        n = 10
        randlist = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
        token = ''.join(randlist)

        cur = conn.cursor()
        chksql = "SELECT * FROM devices where device_name = '" + device_name + "';"
        cur.execute(chksql)
        res = cur.fetchall()
        conn.commit()

        if len(res) == 0:
            sql = "INSERT INTO devices (device_name,description,token) VALUES ('%s','%s','%s');" % (device_name,description,token)
            cur.execute(sql)
            conn.commit()
            cur.close()
            title = 'Complete device registration'
            return render_template('device_registered.html',title=title,token=token,device_name=device_name,description=description)
        else:
            flash(f"{device_name} has already registered.")
            sql = 'SELECT * FROM devices;'
            cur.execute(sql)
            res = cur.fetchall()
            conn.commit()
            cur.close()
            title = "Device Registration"
            return render_template('device_regform.html',title=title,res=res)



@app.route('/log_upload',methods=['POST'])
def log_upload():
    file = request.files.get('file')
    data = request.form.to_dict()
    device_name = data['device_name']
    token = data['token']
    cur = conn.cursor()

    chksql = f"SELECT device_id from devices where device_name = '{device_name}' and token = '{token}';"
    cur.execute(chksql)
    res = cur.fetchall()
    conn.commit()
    
    if len(res) == 1:
        device_id = res[0][0]
        file_name = file.filename
        filename_tosave = device_name + '_' + file_name.split('/')[-1]
        filepath = './log_facecount/' + filename_tosave
        file.save(filepath)

        logs = []
        with open(filepath,'r') as f:
            lines = f.readlines()
            for line in lines:
                if not 'Session Start' in line and not 'Session End' in line and not 'Total Look Count' in line:
                    item = line.split(' - ')[1]
                    logs.append(item)

        insert_list = []
        for logdata in logs:
            logdata = eval(logdata)
            t = (logdata[0],logdata[1],logdata[2],logdata[3],logdata[4],logdata[5],logdata[6],logdata[7],filename_tosave,device_id)
            insert_list.append(t)
        
        
        sql = 'INSERT INTO facecount_log (date,time,session_facecount_id,duration,archive,artid,serial_num,filename,log_filename,device_id) VALUES %s'
        extras.execute_values(cur, sql,insert_list)
        conn.commit()
        cur.close()

        return 'file uploaded successfully.',200

    else:
        cur.close()
        return 'Unauthorized Device.', 403

if __name__ == '__main__':
    app.run()

