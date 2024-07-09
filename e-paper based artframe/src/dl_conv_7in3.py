import subprocess
import requests
import sys
import json
import glob
import os

jsonurl = 'http://artnodes.local/static/current.json'
response = requests.get(jsonurl)
jsondata = response.json()
jsonfilepath = '/home/yosuke/pj-epaper/curate.json'
with open(jsonfilepath,'w') as f:
    f.write(json.dumps(jsondata))


dl_folder = './download/'
bmp_folder = '/bmps73/'

chkfilelist = glob.glob(dl_folder + '*')
if len(chkfilelist) > 0:
    for chkfile in chkfilelist:
        os.remove(chkfile)

if len(jsondata) < 12:
    sys.exit()

for item in jsondata:
    dlurl = item['dlurl']
    savefilepath = dl_folder + item['dlfilename']

    r = requests.get(dlurl)
    with open(savefilepath,'wb') as f:
        f.write(r.content)
    
chkbmpfilelist = glob.glob(bmp_folder + '*')
print(chkbmpfilelist)
if len(chkbmpfilelist) > 0:
    for chkfile in chkbmpfilelist:
        os.remove(chkfile) 

downloadfilelist = glob.glob(dl_folder + '*')

print(downloadfilelist)
for item in downloadfilelist:
    tmp = item.split('/')[-1]
    filename,ext = tmp.split('.')
    bmpfilepath = bmp_folder + filename + '.bmp'
    command = [
        'convert', item,
        '-dither', 'FloydSteinberg',
        '-rotate', '90',
        '-resize', '800x480',
        '-gravity', 'Center',
        '-remap','palette2.png',
        '-extent','800x480',
        
        bmpfilepath

    ]
    # '-rotate', '-90<',
    # '-dither', 'FloydSteinberg',FloydSteinberg
    # '-remap','palette.png',
        
    
    subprocess.run(command,check=True)

if os.path.exists('./current.json'):
    os.remove('./current.json')
