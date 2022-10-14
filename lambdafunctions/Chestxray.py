import json
import requests
import re

def message(img_path):
    req = {'path': img_path}
    result = requests.get('http://EC2_URL?', params=req)
    output = result.text
    

    return output
    
def lambda_handler(event, context):
    img_path= event['queryStringParameters']['q']

    output = message(img_path)

    responseObject = {}
    responseObject['statusCode'] = 200
    responseObject['headers'] = {}
    responseObject['headers']['Content-Type'] = 'application/json'
    responseObject['body'] = json.dumps(output)

    return responseObject
