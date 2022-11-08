import json
import boto3
import uuid

from datetime import datetime
from json_checker import Checker
from requests import get

expected_schema = {'user_id': str, 'funnel': str, "type": str, 'event': str, 'traits': dict, 'properties': dict,
                   'channel': str}


def create_event(event, context):

    try:
        date_storage = datetime.today().strftime('%Y%m%d')

        print(event['body'])

        event_in = json.loads(event['body'])

        checker = Checker(expected_schema)
        checker.validate(event_in)
    except Exception as e:

        response = {
            "statusCode": 400,
            "body": f"{e}"
        }
        return response

    print(event_in, type(event_in))

    s3 = boto3.client('s3')

    id = str(uuid.uuid4())

    ip = event['requestContext']['identity']['sourceIp']

    json_object = {"id": id,
                   'user_id': event_in.get('user_id'),
                   'funnel': event_in.get('funnel'),
                   'type': event_in.get('type'),
                   'event': event_in.get('event'),
                   'traits': json.dumps(event_in.get('traits')),
                   'timestamp': f"{datetime.today()}",
                   'properties': json.dumps(event_in.get('properties')),
                   'channel': event_in.get('channel'),
                   'ip': str(ip)

                   }

    s3.put_object(
        Body=json.dumps(json_object),
        Bucket='reingeniate-data-raw',
        Key=f'events/{date_storage}/{id}.json'
    )

    response = {
        "statusCode": 200,
        "body": f"{json_object}"
    }

    return response


def get_event(event, context):
    response = {
        "statusCode": 200,
        "body": f"{event}"
    }

    return response
