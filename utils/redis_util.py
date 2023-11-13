from redis import Redis
import os
import json

VALID_CHANNEL = [
    "WSS-notif",
    "WSS-comment",
]


def get_redis_connection():
    return Redis(
        host=f"{os.environ.get('REDIS_HOSTNAME', 'localhost')}",
        port=os.environ.get('REDIS_PORT', '6381'),
        # db=os.environ.get('REDIS_DB', '0')
    )


def publish_message_to_wss(channel, data):
    if channel not in VALID_CHANNEL:
        raise ValueError("Invalid channel name")

    if isinstance(data, dict):
        data = json.dumps(data)
    connection = get_redis_connection()
    connection.publish(channel, data)
    return "ok"

# publish_message("hello_world", "hello_world")
