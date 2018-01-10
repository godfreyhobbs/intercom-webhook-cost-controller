import os
import time

import boto3
from boto3.dynamodb.conditions import Attr

EMPTY_STRING = 'EMPTY_STRING'
dynamodb = boto3.resource('dynamodb')


# fix up empty string
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


def save_to_dynamodb(person, conv_count=0, deleted_date=False):
    # fixup
    clean_json(person)
    print('{} {}'.format(person['created_at'], person['id']))

    # must remove floats https://github.com/boto/boto3/issues/665
    if 'location_data' in person:
        if 'latitude' in person['location_data']:
            person['location_data']['latitude'] = str(person['location_data']['latitude'])

        if 'longitude' in person['location_data']:
            person['location_data']['longitude'] = str(person['location_data']['longitude'])

    email = EMPTY_STRING
    if 'email' in person and person['email']:
        email = person['email']

    custom_attr_val = False
    custom_attr_key = os.environ['CUSTOM_ATTR_KEY']
    if 'custom_attributes' in person:
        if custom_attr_key in person['custom_attributes']:
            custom_attr_val = person['custom_attributes'][custom_attr_key]

    person_user_id = '-1'
    if person['user_id']:
        person_user_id = person['user_id']
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    user_data = {'id': person     ['id'],
                 'user_id':       person_user_id,
                 'email':         email,
                 'created_at':    str(person['created_at']),
                 custom_attr_key: custom_attr_val,
                 'body':          (person),
                 'conv_count':    str(conv_count),
                 }
    if deleted_date:
        user_data['deleted_date'] = str(deleted_date)

    return table.put_item(
            Item=user_data
    )


def get_users_with_zero_chats():
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    # consider adding limit to scan
    ## TODO: only delete after 2 days
    twoDaysAgo = int(time.time())- 60*60*24
    filter = Attr('conv_count').eq('0') & Attr('deleted_date').not_exists() & Attr('created_at').lt(str(twoDaysAgo))
    proj = "id, conv_count, created_at, email, deleted_date"
    response = table.scan(
            ProjectionExpression=proj,
            FilterExpression=filter
    )
    data = response['Items']
    while 'LastEvaluatedKey' in response:
        response = table.scan(
                ProjectionExpression=proj,
                FilterExpression=filter,
                ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])
    data = sorted(data, key=lambda x: x['created_at'], reverse=False)
    print("data len [{}]".format(len(data)))
    return data

if __name__ == '__main__':
    print(len(get_users_with_zero_chats()))