import http.client
import json
import os
import random

INTERCOM_BEARER = os.environ['INTERCOM_BEARER']

conn = http.client.HTTPSConnection("api.intercom.io")

headers = {
    'authorization': "Bearer {}".format(INTERCOM_BEARER),
    'accept':        "application/json",
    'content-type':  "application/json",
    'cache-control': "no-cache"
}


def getAllUserWithNoConvs(limit=20000):
    result = []
    # TODO: consider page based genertor
    users = getAllUsers(limit * 10, 'desc')
    user_index = random.sample(range(len(users)),len(users))

    for index in user_index:
        user = users[index]
        if len(result) < limit and not hasConversations(user['id']):
            result.append(user)

    return result


def getAllUsers(limit=20000, sort_direction='asc'):
    result = []

    conn.request("GET", "/users?order={}&sort=updated_at".format(sort_direction), headers=headers)
    res = conn.getresponse()
    output = res.read().decode("utf-8")
    print(output)
    response_json = json.loads(output)
    next_page = response_json['pages']['next']
    result.extend(response_json['users'])
    while (next_page and len(result) < limit):
        conn.request("GET", next_page, headers=headers)
        res = conn.getresponse()
        output = res.read().decode("utf-8")
        print(output)
        response_json = json.loads(output)

        next_page = response_json['pages']['next']
        result.extend(response_json['users'])

    return result


def hasConversations(id):
    conn.request("GET", "/conversations?type=user&intercom_user_id={}".format(id), headers=headers)

    res = conn.getresponse()
    output = res.read().decode("utf-8")
    response_json = json.loads(output)
    print(output)
    return len(response_json['conversations']) > 0


def getUser(id):
    conn.request("GET", "/users/{}".format(id), headers=headers)
    res = conn.getresponse()
    output = res.read().decode("utf-8")
    print(output)
    response_json = json.loads(output)
    return response_json

#
def deletePerson(id):
    print('deleting [{}]'.format(id))

    conn.request("DELETE", "/users/{}".format(id), headers=headers)
    res = conn.getresponse()
    output = res.read().decode("utf-8")
    print(output)
    response_json = json.loads(output)
    return response_json


def getNumToDelete(target_people_count):
    # get counts
    conn.request("GET", "/counts", headers=headers)
    res = conn.getresponse()
    output = res.read().decode("utf-8")
    print(output)
    response_json = json.loads(output)
    people_count = response_json['lead']['count'] + response_json['user']['count']
    result = people_count - target_people_count
    print('numToDelete to reach Target peple count is [{}]'.format(result))
    return result


