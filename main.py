from spreadsheet_client import SpreadsheetClient

from datetime import datetime, timedelta

from slack_sdk import WebClient;
from slack_sdk.errors import SlackApiError;


duty_sheet = SpreadsheetClient('ev-slack-bot-credentials.json', 'EVH RA Fall 24 Duty + More', 'Duty')
move_in_sheet = SpreadsheetClient('ev-slack-bot-credentials.json', 'EVH Fall 24-25 Move-In Shifts', move_in_worksheet='Schedule')

today = datetime.now()# + timedelta(days=4)
display_formatted_date = today.strftime('%B %d, %Y')
abbrev_duty_date = today.strftime('%b %d')
abbrev_move_in_date = (today.strftime(' %m/%d').replace(' 0', '')).replace('/0', '/')
people_on_duty = duty_sheet.get_on_duty(abbrev_duty_date)
try:
    move_in_people = move_in_sheet.get_move_in(abbrev_move_in_date)
except Exception as e:
    print(e)
    move_in_people = None


duty_text = display_formatted_date + "\n"
if move_in_people is not None:
    duty_text += "*Duty:*\n" + people_on_duty + "\n\n*Move In Shifts:*\n" + move_in_people
else:
    duty_text += people_on_duty


# slack authentication & message posting
slack_creds_file = open("ev-slack-app-auth.txt", "r")
client = WebClient(token=slack_creds_file.readline())
try:
    # response = client.chat_postMessage(channel='C07HWAGBVB6', text=duty_text) # Bot channel
    response = client.chat_postMessage(channel='C07EA9N8KUJ', text=duty_text) # Duty info channel
    # assert response["message"]["text"] == "drop dead"
    print(duty_text)
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["ok"] is False
    # assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    print(f"Got an error: {e.response['error']}")






