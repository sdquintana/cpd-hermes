import json
import boto3
import uuid

from datetime import datetime
from json_checker import Checker
from requests import get

from datetime import timedelta
from datetime import datetime
from pyathena import connect
import pandas as pd
import json

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
        Key=f'storyplace/events/{date_storage}/{id}.json'
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


def get_events(event, context):

    try:
        query_parameters = event.get('queryStringParameters')

        if query_parameters is None:
            body = {
                "success": False,
                "message": "queryStringParameters must appear on the api call"
            }

            response = {
                "statusCode": 200,
                "body": json.dumps(body)
            }

            return response

        now = datetime.now()

        start_date = query_parameters.get('start_date')

        end_date = query_parameters.get('end_date')

        if start_date is None or end_date is None:
            body = {
                "success": False,
                "message": "start_date and end_date must appear on the api call"
            }

            response = {
                "statusCode": 200,
                "body": json.dumps(body)
            }

            return response

        check_end = datetime.strptime(end_date, '%Y-%m-%d')

        check_start = datetime.strptime(start_date, '%Y-%m-%d')

        if check_end >= now:
            end_date = now - timedelta(days=1)

        if check_start >= now:
            body = {
                "success": False,
                "message": "start_date must be less than or equal to today"
            }

            response = {
                "statusCode": 200,
                "body": json.dumps(body)
            }

            return response

        conn = connect(s3_staging_dir="s3://reingeniate-artefacts/logs/ ",
                       region_name="us-east-1")
        df = pd.read_sql_query(f"""SELECT   "id"
                                            ,"user_id"
                                            ,"event"
                                            ,"traits"
                                            ,"original_timestamp"
                                            ,"type"
                                            ,"properties"
                                            ,"ip"
                                    FROM warehouse.events_f7d2f9abd018eedc2775bd09de746557
                                    where cast(SUBSTR("original_timestamp",1,10) as date )
                                            between cast('{start_date}' as date) and cast('{end_date}' as date)
                                """, conn)
        response_query = df.to_json(orient='records')

        response = {
            "statusCode": 200,
            "body": f"{response_query}"
        }

        return response
    except Exception as e:

        body = {
            "success": False,
            "message": f"[Error]: {e}"
        }

        response = {
            "statusCode": 500,
            "body": f"{response_query}"
        }

    return response
