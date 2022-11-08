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
        print(e)
        body = {
            "success": False,
            "message": f"{e}"
        }
        response = {
            "statusCode": 400,
            "body": json.dumps(body)
        }
        return response

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
        Bucket='reingeniate-data-raw',
        Key=f'internal/events/{date_storage}/{id}.json'
    )

    body = {
        "success": True,
        "message": json_object
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
