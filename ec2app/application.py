import os,sys
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
import argparse
import skimage, skimage.io
import pprint
import torch
import torch.nn.functional as F
import torchvision, torchvision.transforms
import torchxrayvision as xrv
import json
from flask import json,request,Flask,make_response,jsonify
import requests
import boto3
import cv2

# Create an S3 access object
s3 = boto3.client("s3")
#weight file
weights = "densenet121-res224-all"
#transform for cropping
transform = torchvision.transforms.Compose([xrv.datasets.XRayCenterCrop()])
#load weight file
model = xrv.models.get_model(weights)
app = Flask(__name__)

def prob(values,output):
    result = round(output['preds'][values] * 100)
    if result >=50:

        output = str(result) + "%" + ' ' + "probability of" + ' ' + values
    else:
        output = ' '
    return output


# route http posts to this method
@app.route('/interact', methods=['POST','GET'])
def test():
    # the search query you want
    img_path = request.args.get('path')
    split_tup = os.path.splitext(img_path)

    file_extension = split_tup[1]
    if file_extension == ".png":
        s3.download_file(Bucket="bucketname", Key=img_path, Filename="input.png")
        image = cv2.imread('input.png')

        # Save .jpg image
        cv2.imwrite('input.jpg', image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

    elif file_extension == ".jpg":
        s3.download_file(Bucket="bucketname", Key=img_path, Filename="input.jpg")

    img = skimage.io.imread("input.jpg")
    img = xrv.datasets.normalize(img, 255)  

    # Check that images are 2D arrays
    if len(img.shape) > 2:
        img = img[:, :, 0]
    if len(img.shape) < 2:
        print("error, dimension lower than 2 for image")

    # Add color channel
    img = img[None, :, :]
    img = transform(img)

    output = {}
    with torch.no_grad():
        img = torch.from_numpy(img).unsqueeze(0)
        preds = model(img).cpu()
        output["preds"] = dict(zip(xrv.datasets.default_pathologies,preds[0].detach().numpy()))
    
    Atelectasis = prob('Atelectasis',output)
    Cardiomegaly = prob( 'Cardiomegaly',output)
    Consolidation = prob('Consolidation',output)
    Edema = prob('Edema',output)
    Effusion = prob('Effusion',output)
    Emphysema = prob('Emphysema',output)
    Enlarged_Cardiomediastinum = prob('Enlarged Cardiomediastinum',output)
    Fibrosis = prob('Fibrosis',output)
    Fracture = prob('Fracture',output)
    Hernia= prob('Hernia',output)
    Infiltration = prob('Infiltration',output)
    Lung_Lesion = prob('Lung Lesion',output)
    Lung_Opacity = prob('Lung Opacity',output)
    Mass = prob('Mass',output)
    Nodule = prob('Nodule',output)
    Pleural_Thickening = prob('Pleural_Thickening',output)
    Pneumonia = prob('Pneumonia',output)
    Pneumothorax = prob('Pneumothorax',output)
    results = Atelectasis + ' ' + Cardiomegaly + ' ' + Consolidation + ' ' + Edema + ' ' + Effusion + ' ' + Emphysema + ' ' + Enlarged_Cardiomediastinum + ' ' + Fibrosis + ' ' +Fracture +' ' + Hernia + ' ' +Infiltration + ' ' + Lung_Lesion + ' ' +Lung_Opacity + ' ' + Mass + ' ' +Nodule +' ' +Pleural_Thickening + ' ' + Pneumonia + ' ' +Pneumothorax

    os.remove("input.jpg")
    return json.dumps(str(results))
if __name__ == "__main__":
        app.run()

