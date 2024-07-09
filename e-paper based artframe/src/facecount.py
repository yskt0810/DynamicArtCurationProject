import cv2
import dlib
import numpy as np
import time
import signal
import json
import csv
import os
from datetime import datetime as dt

# デバッグモードの設定
DEBUG_MODE = True

# ログファイルの設定
log_file = f"./logs/look_log_{time.strftime('%Y%m%d_%H%M%S')}.csv"

# E-PAPER表示データJSON
epaper_currentpath = '/home/yosuke/pj-epaper/current.json'

# Dlibの顔検出器と顔のポーズ推定器を初期化
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# カメラを初期化
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# フレームレートを15 FPSに設定
cap.set(cv2.CAP_PROP_FPS, 15)

look_count = 0
look_start_time = None
is_looking = False

def log_and_debug(message):
    global log_file
    if not os.path.exists(log_file):
        log_file = f"./logs/look_log_{time.strftime('%Y%m%d_%H%M%S')}.csv"

    with open(log_file, "a") as log:
        log.write(f"{time.strftime('%Y/%m/%d %H:%M:%S')} - {message}\n")
    if DEBUG_MODE:
        print(message)

def handle_exit(signum, frame):
    global is_looking, look_start_time, look_count,log_file

    if not os.path.exists(log_file):
        log_file = f"./logs/look_log_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    
    if is_looking:
        look_duration = time.time() - look_start_time
        log_and_debug(f"Look {look_count}: Duration {look_duration:.2f} seconds")
    log_and_debug(f"Session End {time.strftime('%Y/%m/%d %H:%M:%S')}")
    log_and_debug(f"Total Look Count: {look_count}")
    cap.release()
    exit(0)

# シグナルハンドラの設定
signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

log_and_debug(f"Session Start {time.strftime('%Y/%m/%d %H:%M:%S')}")

#try:
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 1秒ごとにフレームを処理
    time.sleep(0.1)
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    if DEBUG_MODE:
        debug_message = "No faces detected" if len(faces) == 0 else f"{len(faces)} face(s) detected"
        print(debug_message)

    current_looking = False
    for face in faces:
        shape = predictor(gray, face)
        nose_point = np.array((shape.part(33).x, shape.part(33).y))
        chin_point = np.array((shape.part(8).x, shape.part(8).y))
        vector = chin_point - nose_point
        direction = vector / np.linalg.norm(vector)

        if abs(direction[0]) < 0.15:  # 顔が正面を向いていると判断
            current_looking = True
            if not is_looking:
                is_looking = True
                look_start_time = time.time()
                look_count += 1
            break
    
    if not current_looking and is_looking:
        is_looking = False
        look_duration = time.time() - look_start_time

        if look_duration > 2.0:
            with open(epaper_currentpath,'r') as f:
                epaper_current = json.load(f)
            
            recordtime = dt.now()
            record_date = recordtime.strftime('%Y-%m-%d')
            record_time = recordtime.strftime('%H:%M:%S')
            recorddata = [record_date,record_time,look_count,f"{look_duration:.2f}",epaper_current['archive'],epaper_current['artid'],epaper_current['serial_num'],epaper_current['dlfilename']]
            
            #log_and_debug(f"Look {look_count}: Duration {look_duration:.2f} seconds")
            log_and_debug(recorddata)
            

#finally:
#    handle_exit(None, None)
