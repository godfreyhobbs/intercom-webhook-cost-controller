import os

import boto3
import intercomClient

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

def save_to_dynamodb(person):
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
    if 'email' in person and  person['email']:
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
    return table.put_item(
        Item={
            'id': person['id'],
            'user_id': person_user_id,
            'email': email,
            'created_at': str(person['created_at']),
            custom_attr_key: custom_attr_val,
            'body': (person)
        }
    )

# if __name__ == '__main__':
    # run to catch up.  Adds all existing users to dynamodb
    # limit = 20000
    # users_json = intercomClient.getAllUsers(limit)
    # print (users_json)
    #
    # for person in users_json:
    #      print(save_to_dynamodb(person))