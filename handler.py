import json
from decimal import *
import boto3
from botocore.errorfactory import ClientError
import os


EMPTY_STRING = 'EMPTY_STRING'

dynamodb = boto3.resource('dynamodb')

def clean_json(node):
    for key, item in node.items():

        if isinstance(item, dict):
            clean_json(item)
        elif isinstance(item, list):
            for index, elem in enumerate(item):
                if isinstance(elem, dict):
                    clean_json(elem)
                elif elem == '':
                    item[index] = EMPTY_STRING
        else:
            for key, item in node.items():
                # print item
                if item == '':
                    node[key] = EMPTY_STRING

def save_to_dynamodb(person):
    # fixup
    clean_json(person)
    print('{} {}'.format(person['created_at'], person['id']))

    # must remove floats https://github.com/boto/boto3/issues/665
    if 'location_data' in person:
        if 'latitude' in person['location_data']:
            person['location_data']['latitude'] = Decimal(str(person['location_data']['latitude']))

        if 'longitude' in person['location_data']:
            person['location_data']['longitude'] = Decimal(str(person['location_data']['longitude']))

    email = ''
    if 'email' in person:
        email = person['email']
    custom_attr = False
    custom_attr_key = os.environ['CUSTOM_ATTR_KEY']
    if 'custom_attributes' in person:
        if custom_attr_key in person['custom_attributes']:
            custom_attr = person['custom_attributes'][custom_attr_key]

    table = dynamodb.Table('bd-ai-intercom-people')
    table.put_item(
        Item={
            'id': person['id'],
            'user_id': person['user_id'],
            'email': email,
            'created_at': person['created_at'],
            custom_attr_key: custom_attr,
            'body': (person)
        }
    )


def webhook(event, context):
    print(os.environ['DYNAMODB_TABLE'])

    print(json.dumps(event))
    print(event['body'])

    webhook_body = json.loads(event['body']);

    save_to_dynamodb(webhook_body['data']['item']);

    response = {
        "statusCode": 200,
        "body": json.dumps({
            "message": "function executed successfully!",
            "input": event
        })
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
