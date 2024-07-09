import sys
import os
import glob
import json
picdir = '/home/yosuke/pj-epaper'
libdir = '/home/yosuke/pj-epaper/lib'
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in3f
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG,format="%(asctime)s - %(levelname)s:%(name)s - %(message)s",
filename="epaper73-ctl.log")

if os.path.exists('/home/yosuke/pj-epaper/current.json'):
    with open('/home/yosuke/pj-epaper/current.json','r') as f:
        currentdata = json.load(f)
else:
    with open('/home/yosuke/pj-epaper/curate.json','r') as f:
        tmp = json.load(f)
        currentdata = tmp[0]

if os.path.exists('/home/yosuke/pj-epaper/curate.json'):
    with open('/home/yosuke/pj-epaper/curate.json','r') as f:
        curatedata = json.load(f)
else:
    logging.info('Curate Data does not exist.')
    sys.exit()

current_id = currentdata['index']
if 'next_id' in currentdata:
    next_id = currentdata['next_id']
else:
    next_id = 0

logging.info(f"Current ID is {current_id}, Next ID is {next_id}. ")

if current_id == 0 and next_id == 0:
    readfile = currentdata['dlfilename'].split('.')[0] + '.bmp'
    targetdata = curatedata[current_id]
    targetdata['next_id'] = 1    
else:
    targetid = next_id
    if targetid > 12:
        targetid = 0
    
    targetdata = curatedata[targetid]
    readfile = targetdata['dlfilename'].split('.')[0] + '.bmp'
    targetdata['next_id'] = targetid + 1


### E-PAPER Control Section

try:
    logging.info("===== epd5in65 exec start =====")

    epd = epd7in3f.EPD()
    logging.info("epd5in65 init and clear")
    epd.init()
    epd.Clear()

    logging.info(f"epd5in65 read bmp file {readfile}")
    Himage = Image.open('/home/yosuke/pj-epaper/bmps73/' + readfile)
    Himage = Himage.transpose(Image.ROTATE_90)
    epd.display(epd.getbuffer(Himage))

    logging.info("epd5in65 Goto Sleep....")
    epd.sleep()

    logging.info("===== epd5in65 exec finished =====")

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c")
    epd5in65f.epdconfig.module_exit()
    exit()

with open('/home/yosuke/pj-epaper/current.json','w') as f:
    f.write(json.dumps(targetdata))
