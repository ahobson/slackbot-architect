import json


def handler(req, context):
    """Slack endpoint"""
    return {
        "statusCode": 403,
        "body": json.dumps({}),
        "headers": {"Content-type": "application/json"},
    }
