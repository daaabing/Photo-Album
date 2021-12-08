
import json
import boto3
import requests
from requests_aws4auth import AWS4Auth
from requests.auth import HTTPBasicAuth 

region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
HTTPBasicAuth
# url = 'https://vpc-a2photos-vvsv5lqfof5dwmysbvnkemfyum.us-east-1.es.amazonaws.com/photos/_search'
url = 'https://search-photospublic-auby3bgv6zqfvqslrnilfbug6a.us-east-1.es.amazonaws.com/photos/_search'
headers = { "Content-Type": "application/json" }
lexruntime = boto3.client('lex-runtime')
def lambda_handler(event, context):
    response = lexruntime.post_text(
        botName='QueryBot',
        botAlias='$LATEST',
        userId='test',
        inputText = event["queryStringParameters"]["q"],
        sessionAttributes={},
    )
    slots = response['slots']["query"].split()
    # slots = [event["queryStringParameters"]["q"]]
    print(slots)
    slots = [{ "match": { "labels":  s} } for s in slots]
    params = {
        "query": {
            "function_score": {
                "query": { "bool": { "should": slots } },
                "random_score": {}
            }
        }
    }
    r = requests.get(url, auth=HTTPBasicAuth("", ""), data=json.dumps(params), headers=headers)
    # r = requests.get(url, auth=awsauth, data=json.dumps(params), headers=headers)
    r = json.loads(r.text)
    print(r)
    r = r['hits']['hits']
    res = [o["_source"]["objectKey"] for o in r]
    print(res)
    
    return {
        "statusCode": 200,
        "headers": {
            'Content-Type': 'application/json',
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*"
        },
        "body": json.dumps(res)
    }
            # "Access-Control-Allow-Origin": "http://chatbot6998cc.s3-website-us-east-1.amazonaws.com",


    