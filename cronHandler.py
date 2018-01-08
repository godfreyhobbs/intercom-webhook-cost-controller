from intercomClient import getNumToDelete, getAllUserWithNoConvs, deletePerson
from dynamodbClient import save_to_dynamodb
# Value is set to keep cost under the 2000 user limit
TARGET_PEOPLE_COUNT = 2000

def deleteUsers(event, context):
    # setting low due to rate limiting errors
    limit = 200
    num_to_delete = min(getNumToDelete(TARGET_PEOPLE_COUNT), limit)
    users_json = getAllUserWithNoConvs(num_to_delete)
    print('{} people will be deleted'.format(len(users_json)))
    for person in users_json:
        print(save_to_dynamodb(person))
        print('deleting {}'.format(person['id']))
        print(deletePerson(person['id']))

if __name__ == '__main__':
    # delete users so as not to be charged by intercoms pricing model.
    deleteUsers({},{})
