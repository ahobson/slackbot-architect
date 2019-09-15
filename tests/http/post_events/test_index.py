import json
import os.path
import sys

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "../../../src/http/post-events"
        )
    ),
)

import index


def test_handler():

    event = {"headers": {}}
    r = index.handler(event, {})
    assert r["body"] is not None
    rj = json.loads(r["body"])
    assert rj is not None
