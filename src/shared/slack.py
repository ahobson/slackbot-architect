# Most of this code is copied from
#
# https://github.com/slackapi/python-slack-events-api/blob/master/slackeventsapi/server.py
# That code assumes using flask, but we're using a lambda so we can't
# really reuse it effectively.

import hmac
import hashlib
import time


def verify_signature(timestamp, signature, request_data, signing_secret):
    # Verify the request signature of the request sent from Slack
    # Generate a new hash using the app's signing secret and request data

    req = "v0:" + str(timestamp) + ":" + request_data
    request_hash = (
        "v0="
        + hmac.new(
            str.encode(signing_secret), req.encode(), hashlib.sha256
        ).hexdigest()
    )
    return hmac.compare_digest(request_hash, signature)


def verify_event(event, signing_secret):
    # Each request comes with request timestamp and request signature
    # emit an error if the timestamp is out of range
    req_timestamp = event["headers"].get("X-Slack-Request-Timestamp", "0")
    if abs(time.time() - int(req_timestamp)) > 60 * 5:
        return "Invalid request timestamp"

    # Verify the request signature using the app's signing secret
    # emit an error if the signature can't be verified
    req_signature = event["headers"].get("X-Slack-Signature", "0")
    if not verify_signature(
        req_timestamp, req_signature, event["body"], signing_secret
    ):
        return "Invalid request signature"

    return None
