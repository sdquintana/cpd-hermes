import json
import boto3
import uuid

from datetime import datetime
from json_checker import Checker
from requests import get

expected_schema = {'user_id': int, 'event': str, 'traits': dict, 'properties': dict}


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

    id = str(uuid.uuid4())


    ip = event['requestContext']['identity']['sourceIp']


    json_object = {"id": id,
                   "user_id": event_in.get('user_id'),
                   "event": event_in.get('event'),
                   'traits': event_in.get('traits'),
                   'original_timestamp': f"{datetime.today()}",
                   'type': 'track',
                   'properties': json.dumps(event_in.get('properties')),
                   'ip': str(ip)
                   }
    s3.put_object(
        Body=json.dumps(json_object),
        Bucket='cpd-data-raw',
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
