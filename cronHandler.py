import intercomClient
from dynamodbClient import save_to_dynamodb, get_users_with_zero_chats

# Value is set to keep cost under the 2000 user limit
TARGET_PEOPLE_COUNT = 2000

def deleteUsers(event, context):
    # setting low due to rate limiting errors
    LIMIT = 500
    num_to_delete = min(intercomClient.getNumToDelete(TARGET_PEOPLE_COUNT), LIMIT)

    users_data = get_users_with_zero_chats()

    for curr_person in users_data[:num_to_delete]:
        print("person [{}]".format(curr_person['id']))
        # time.sleep(.3)
        try:
            conv_count = intercomClient.get_conversation_count(curr_person['id'])
            user = intercomClient.getUser(curr_person['id'])
            print(save_to_dynamodb(user, conv_count))
            if (conv_count == 0):
                print(intercomClient.deletePerson(user['id']))

        except:
            print("failure for [{}]".format(curr_person['id']))


# if __name__ == '__main__':
    # delete users so as not to be charged by intercoms pricing model.
    # deleteUsers({}, {})
