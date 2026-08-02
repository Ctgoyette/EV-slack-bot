from spreadsheet_client import SpreadsheetClient

from datetime import datetime, timedelta
import requests
import json

from slack_sdk import WebClient;
from slack_sdk.errors import SlackApiError;

OUTPUT_PLATFORM = 'Teams'


duty_sheet = SpreadsheetClient('ev-slack-bot-credentials.json', 'EV CA Summer 26 Duty + More', duty_worksheet='Duty')
move_in_sheet = SpreadsheetClient('ev-slack-bot-credentials.json', 'EVH Spring 25-26 Move-In Shifts', move_in_worksheet='Schedule')

today = datetime.now() #+ timedelta(days=4)
display_formatted_date = today.strftime('%B %d, %Y')
abbrev_duty_date = today.strftime('%b %d')
abbrev_move_in_date = (today.strftime(' %m/%d').replace(' 0', '')).replace('/0', '/')
abbrev_move_out_date = (today.strftime('%m/%d'))
people_on_duty = duty_sheet.get_on_duty(abbrev_duty_date)
try:
    move_in_people = move_in_sheet.get_move_in(abbrev_move_in_date)
except Exception as e:
    print(e)
    move_in_people = None

try:
    move_out_people = duty_sheet.get_move_out(abbrev_move_in_date)
except Exception as e:
    print(e)
    move_out_people = None


duty_text = display_formatted_date + "\n"
if move_in_people is not None:
    duty_text += "*Duty:*\n" + people_on_duty + "\n\n*Move In Shifts:*\n" + move_in_people
elif move_out_people is not None:
    duty_text += "*Duty:*\n" + people_on_duty + "\n\n*Move Out Shifts:*\n" + move_out_people
else:
    duty_text += people_on_duty

if OUTPUT_PLATFORM == 'Slack':
    # slack authentication & message posting
    slack_creds_file = open("ev-slack-app-auth.txt", "r")
    client = WebClient(token=slack_creds_file.readline())
    try:
        # response = client.chat_postMessage(channel='C0B4LGKMZE2', text=duty_text) # Bot channel
        # response = client.chat_postMessage(channel='C0B11S37CDS', text=duty_text) # Duty info channel
        # assert response["message"]["text"] == "drop dead"
        print(duty_text)
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        # assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")
elif OUTPUT_PLATFORM == 'Teams':
    webhook_url = open("teams-webhook.txt", "r").readline()

    message = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "type": "AdaptiveCard",
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": display_formatted_date,
                            "weight": "Bolder",
                            "size": "Large",
                            "wrap": True
                        },
                        {
                            "type": "TextBlock",
                            "text": people_on_duty,
                            "wrap": True
                        }
                    ]
                }
            }
        ]
    }

    response = requests.post(
        webhook_url,
        data=json.dumps(message),
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        print("Message sent successfully")
    else:
        print(f"Failed to send message: {response.status_code}, {response.text}")







