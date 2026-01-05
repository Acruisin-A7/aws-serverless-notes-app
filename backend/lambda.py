import json
import boto3
import uuid
from datetime import datetime
import os
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')

# Table name should always come from environment variables in real deployments
TABLE_NAME = os.environ.get('DYNAMODB_TABLE', '<your-table-name>')
table = dynamodb.Table(TABLE_NAME)

def cors_headers():
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type,x-device-id'
    }

def get_device_id(event):
    headers = event.get('headers', {}) or {}
    device_id = headers.get('x-device-id') or headers.get('X-Device-Id')

    if not device_id:
        body = event.get('body')
        if body:
            try:
                payload = json.loads(body)
                device_id = payload.get('device_id')
            except json.JSONDecodeError:
                pass

    if not device_id:
        raise ValueError("Device ID is required")

    return device_id.strip()

def lambda_handler(event, context):
    print("Incoming event:", json.dumps(event))

    route_key = event.get('routeKey', '')
    method_path = route_key.split(' ')
    if len(method_path) == 2:
        method, path = method_path
    else:
        method = event.get('requestContext', {}).get('http', {}).get('method')
        path = event.get('rawPath', '')

    path_params = event.get('pathParameters') or {}

    try:
        if method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': ''
            }

        device_id = get_device_id(event)

        # CREATE NOTE
        if path == '/notes' and method == 'POST':
            body = json.loads(event.get('body', '{}'))
            title = body.get('title', '').strip()
            content = body.get('content', '').strip()

            if not title or not content:
                raise ValueError("Title and content are required")

            note_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()

            table.put_item(Item={
                'note_id': note_id,
                'device_id': device_id,
                'title': title,
                'content': content,
                'created_at': now,
                'updated_at': now
            })

            return {
                'statusCode': 201,
                'headers': cors_headers(),
                'body': json.dumps({'note_id': note_id})
            }

        # LIST NOTES (by device)
        elif path == '/notes' and method == 'GET':
            response = table.query(
                IndexName='<device-id-gsi-name>',
                KeyConditionExpression=Key('device_id').eq(device_id)
            )

            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps(response.get('Items', []))
            }

        # SINGLE NOTE OPERATIONS
        elif path.startswith('/notes/'):
            note_id = path_params.get('id')
            if not note_id:
                raise ValueError("Missing note ID")

            response = table.get_item(Key={'note_id': note_id})
            item = response.get('Item')

            if not item or item.get('device_id') != device_id:
                raise ValueError("Note not found or access denied")

            if method == 'GET':
                return {
                    'statusCode': 200,
                    'headers': cors_headers(),
                    'body': json.dumps(item)
                }

            elif method == 'PUT':
                body = json.loads(event.get('body', '{}'))
                title = body.get('title', '').strip()
                content = body.get('content', '').strip()

                if not title or not content:
                    raise ValueError("Title and content are required")

                now = datetime.utcnow().isoformat()

                table.update_item(
                    Key={'note_id': note_id},
                    UpdateExpression="SET title = :t, content = :c, updated_at = :u",
                    ExpressionAttributeValues={
                        ':t': title,
                        ':c': content,
                        ':u': now
                    }
                )

                return {
                    'statusCode': 200,
                    'headers': cors_headers(),
                    'body': json.dumps({'message': 'Updated'})
                }

            elif method == 'DELETE':
                table.delete_item(Key={'note_id': note_id})
                return {
                    'statusCode': 204,
                    'headers': cors_headers(),
                    'body': ''
                }

        return {
            'statusCode': 404,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Not found'})
        }

    except ValueError as ve:
        return {
            'statusCode': 400,
            'headers': cors_headers(),
            'body': json.dumps({'error': str(ve)})
        }

    except Exception as e:
        print("Unhandled error:", str(e))
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Server error'})
        }
