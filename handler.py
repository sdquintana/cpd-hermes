import json
import boto3
import uuid

from datetime import datetime


def create_event(event, context):
    date_storage = datetime.today().strftime('%Y%m%d')

    print(event['body'])

    event_in = json.loads(event['body'])

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
