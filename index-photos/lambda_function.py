import json
import urllib
import boto3
import requests
from requests_aws4auth import AWS4Auth
from requests.auth import HTTPBasicAuth 
region = 'us-east-2'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

# url = 'https://vpc-a2photos-vvsv5lqfof5dwmysbvnkemfyum.us-east-1.es.amazonaws.com/photos/_doc'
url = 'https://search-photos-wf47syehoy53qwgudl3fepdp2u.us-east-2.es.amazonaws.com/photos/_doc'
headers = { "Content-Type": "application/json" }
s3 = boto3.client('s3')

def detect_labels(photo, bucket):
    client=boto3.client('rekognition')
    response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}}, MaxLabels=10)
    labels = []
    for label in response['Labels']:
        labels.append(label['Name'])
    print('labels',labels)
    return labels

def lambda_handler(event, context):
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    photo = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    print(bucket, photo)
    try:
        # response = s3.get_object(Bucket=bucket, Key=photo)
        labels = detect_labels(photo, bucket)
        meta = s3.head_object(Bucket=bucket, Key=photo)
        print("meta:", meta)
        if "customlabels" in meta["Metadata"]:
            labels += meta["Metadata"]["customlabels"].split(",")
        
        labels = json.dumps(labels)
        doc = {
            "objectKey": photo,
            "bucket": bucket,
            "createdTimestamp": str(meta["LastModified"]),
            "labels": labels
        }
        print(doc)
        # r = requests.post(url, auth=awsauth, json=doc, headers=headers)
        r = requests.post(url, auth=HTTPBasicAuth("", ""), json=doc, headers=headers)
        r = json.loads(r.text)
        return doc
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(photo, bucket))
        raise e

