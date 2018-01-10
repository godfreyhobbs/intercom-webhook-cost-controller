import json
import os

from dynamodbClient import save_to_dynamodb
import intercomClient

def webhook(event, context):
    print(os.environ['DYNAMODB_TABLE'])
    print(json.dumps(event))
    print(event['body'])

    webhook_body = json.loads(event['body']);
    person = webhook_body['data']['item']
    #fetch using the intercom rest ap, since the webhook object model does not have consistent types for timestamps

    conv_count = intercomClient.get_conversation_count(person['id'])
    save_to_dynamodb(intercomClient.getUser(person['id']), conv_count);

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