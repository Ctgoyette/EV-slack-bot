import os;

from slack_sdk import WebClient;
from slack_sdk.errors import SlackApiError;


client = WebClient(token='Slack-bot-authentication-token')

try:
    response = client.chat_postMessage(channel="#test", text="drop dead")
    # assert response["message"]["text"] == "drop dead"
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["ok"] is False
    # assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    print(f"Got an error: {e.response['error']}")