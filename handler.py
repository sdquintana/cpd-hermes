import json
import boto3
import uuid

from datetime import datetime
from json_checker import Checker

expected_schema = {'user_id': int, 'event': str}


def create_event(event, context):

    try:
        date_storage = datetime.today().strftime('%Y%m%d')

        print(event['body'])

        event_in = json.loads(event['body'])

        checker = Checker(expected_schema)
        checker.validate(event_in)
    except Exception as e:
        print(e)
        response = {
            "statusCode": 400,
            "body": "wrong input"
        }
        return response

    print(event_in, type(event_in))

    s3 = boto3.client('s3')
    json_object = {"user_id": event_in.get('user_id'), "event": event_in.get('event')}
    s3.put_object(
        Body=json.dumps(json_object),
        Bucket='cpd-data-raw',
        Key=f'events/{date_storage}/{str(uuid.uuid4())}.json'
    )

    response = {
        "statusCode": 200,
        "body": f"{event['body']}"
    }

    return response


def get_event(event, context):
    response = {
        "statusCode": 200,
        "body": f"{event}"
    }

    return response
