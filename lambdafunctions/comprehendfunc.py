import json
import boto3
text_out = []
def detect_text(photo, bucket):
    # Document
    s3BucketName = bucket
    documentName = photo
    Comprehend_client = boto3.client('comprehendmedical')
  

    # Amazon Textract client
    textract = boto3.client('textract')
    s3_client = boto3.client('s3')


    # Call Amazon Textract
    response = textract.detect_document_text(
        Document={
            'S3Object': {
                'Bucket': s3BucketName,
                'Name': documentName
            }
        })

    #print(response)
    output = []
    # Print detected text
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            result = item["Text"]
            output.append(result)
    output = ' '.join(output)

  
    try:
        result = Comprehend_client.detect_entities(Text=output )
        resEntities = result['Entities'];
        resText = [i['Text'] for i in resEntities]
        resCategories = [i['Category'] for i in resEntities]
        entDict = dict(zip(resText, resCategories))
        return entDict
    except:
        return output
  


       
def lambda_handler(event, context):
    Text= event['queryStringParameters']['t']
    bucket='bucketname'
    text=detect_text(Text, bucket)
    responseObject = {}
    responseObject['statusCode'] = 200
    responseObject['headers'] = {}
    responseObject['headers']['Content-Type'] = 'application/json'
    responseObject['body'] = json.dumps(text)

    return responseObject

