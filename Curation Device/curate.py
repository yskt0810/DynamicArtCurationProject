import os
import cv2
import torch
import numpy as np
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms
import torchvision.models as models
from PIL import Image
import time
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
import requests
import json
import glob
import os,sys

class CustomeResNet50(nn.Module):
  def __init__(self,num_classes=10):
    super(CustomeResNet50,self).__init__()

    self.resnet50 = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)

    num_features = self.resnet50.fc.in_features
    self.resnet50.fc = nn.Linear(num_features, num_classes)
  
  def forward(self,x):
    return self.resnet50(x)


standbyfolder = '../static/standby/'
completefolder = '../static/complete/'

dlfilefolder = '../static/downloads/'
targets = glob.glob(standbyfolder + '*')

print(targets)
if len(targets) == 0:
    print("No files are standby.... program exit.")
    sys.exit()

targetfilepath = targets[0]
targetfilename = targetfilepath.split('/')[-1]
serial_num = targetfilename.split('.')[0] + '/'
if not os.path.exists(dlfilefolder + serial_num):
    os.mkdir(dlfilefolder + serial_num)

def resize_maintain_aspect_ratio(image, width, height):
    # アスペクト比を維持したまま画像をリサイズ
    orig_height, orig_width = image.shape[:2]
    aspect_ratio = orig_width / orig_height
    target_aspect_ratio = width / height
    
    if aspect_ratio > target_aspect_ratio:
        # 幅を基準にリサイズ
        new_width = width
        new_height = int(width / aspect_ratio)
    else:
        # 高さを基準にリサイズ
        new_height = height
        new_width = int(height * aspect_ratio)
        
    resized_image = cv2.resize(image, (new_width, new_height))
    
    # 余白を追加
    top = (height - new_height) // 2
    bottom = height - new_height - top
    left = (width - new_width) // 2
    right = width - new_width - left
    
    resized_with_padding = cv2.copyMakeBorder(resized_image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[255, 255, 255])
    
    return resized_with_padding

# データ設定
#label_list = ['1','2','3','5','7','8','9','10','11','99']
label_list = ['1','2','3']

# Model Configuration
transform_size = 224
modelpath = './models/' # write your pytorch model path 

model = CustomeResNet50(num_classes=10) # define your model architecture and classnum. 

# load sate dict
model.load_state_dict(torch.load(modelpath))

# Cretation, optimizer and transform: 
#  set appropriate parameters for your models

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters())

transform = transforms.Compose([
#    transforms.Resize((transform_size,transform_size)),
#    transforms.ToTensor(),
#    transforms.Normalize(mean=[0.485, 0.456, 0.406],
#                         std=[0.229, 0.224, 0.225]),
])

img = cv2.imread(targetfilepath)
img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
target_width = transform_size
target_height = transform_size
result_image = resize_maintain_aspect_ratio(img,target_width,target_height)
pilimg = Image.fromarray(result_image)
img_in = transform(pilimg)
img_in = img_in.unsqueeze(0)

model.eval()
output = model(img_in)
_,predicted = torch.max(output,1)
label = label_list[predicted[0].item()]

vals = output[0].tolist()

print('class: ', label)
count = 0
for val in vals:
    print('class' ,count, ' : ', val)
    count = count + 1

### TSNE Source Data読み込み

tsne_src = pd.read_csv('./data/sample.csv',index_col=0,header=0)
# Write the Path to CSV file of your model pre-score data. 
# Could refer the Sample file at ./data/sample.csv

target_vals = vals + [label]
tsne_src.loc[targetfilepath] = target_vals
filelists = tsne_src.index.tolist()
tsne_src = tsne_src.drop(columns='label')

tsne = TSNE(n_components=2,random_state=0)
scaler = StandardScaler()
tscore_base = scaler.fit_transform(tsne_src[label_list].to_numpy())
tscore = tsne.fit_transform(tscore_base)

tscore_df = pd.DataFrame(data=tscore.tolist(),columns=['x','y'])
tscore_df['file'] = filelists
tscore_df = tscore_df.set_index('file')

tscore = tscore_df.loc[targetfilepath].tolist()

# This is the sample to send the score to the API. Here should modify as you want.

senddata = {
    "label": int(label),
    "tsne_x": tscore[0],
    "tsne_y": tscore[1],
    "nums": 12
}

json_data = json.dumps(senddata)
print(json_data)
header = { "Content-Type": "application/json" }
response = requests.post(
    url='', # URL to the API endpoint to post the score in your art archive.
    data=json_data,
    headers=header
)
resdata = json.loads(json.dumps(response.json()))

artwork_list = []

for count,item in enumerate(resdata):

    # Write here the code to
    # - download artwork images from the resdata
    # - store the resdata into your postgreSQL database
    

    # The following is the sample code to download and store the data
    # in case that the art archive provide the image download with spicifying archive ID and artwork ID as POST method.
    
    print(count,item)
    dlurl = '' # URL for download artwork image from the archive
    senddata = {
        "token":"",
        "archive": item[0],
        "artid": item[1]
    }
    json_data = json.dumps(senddata)
    header = {"Content-Type":"application/json"}
    response = requests.post(
        url=dlurl,
        data=json_data,
        headers=header
    )
    imgdata = response.content
    dlfilename = 'dl_' + str(item[0]) + '_' + str(item[1]) + '.jpg'
    savepath = dlfilefolder + serial_num + dlfilename
    with open(savepath,'wb') as f:
        f.write(imgdata)
    
    # The following is the sample code to save artwork information into JSON file (current.json)
    # The API return the following data
    # 
    # "archive": archive ID
    # "artid": artwork ID
    # "title": title of artwork 
    # "artist": artist name
    # "metrics": Eucride Distance Score form the target (evaluated) artworks
    # "label": Classification label of the artwork
    # "dlurl": URL of the artwork image


    dlfile_url = 'http://artnodes.local/static/downloads/' + serial_num + dlfilename
    artwork_data = {
        "index": count,
        "archive": item[0],
        "artid": item[1],
        "title": item[2],
        "artist": item[3],
        "metrics": item[5],
        "label": item[6],
        "model": "ATZ_ABST",
        "dlurl": dlfile_url,
        "serial_num": str(serial_num).replace('/',''),
        "dlfilename": dlfilename

    }
    artwork_list.append(artwork_data)
    time.sleep(1)

os.replace(standbyfolder + targetfilename, completefolder + targetfilename)

jsonoutpath = '../static/current.json'
with open(jsonoutpath,'w') as f:
    json.dump(artwork_list,f,indent=4)
