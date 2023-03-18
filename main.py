from datetime import datetime
import gspread

from slack_sdk import WebClient;
from slack_sdk.errors import SlackApiError;

# call google spreadsheet
gc = gspread.service_account(filename='../ev-slack-bot-credentials.json')
sheet = gc.open('EVHMH RA Spring 2023 Duty + More')
duty_worksheet = sheet.worksheet('Duty')
    
# finds the people on duty for the given date
def get_on_duty(date):
    try:
        target_row = duty_worksheet.find(date).row
        person_one = duty_worksheet.cell(target_row, 6).value
        person_two = duty_worksheet.cell(target_row, 7).value
        duty_string = '{} & {}'.format(person_one, person_two)
        return(duty_string)
    except:
        return("Looks like we have the day off! Jk, somebody should probabaly figure out who's on duty")

today = datetime.now()
abbrev = today.strftime('%b %d').replace(' 0', ' ')
people_on_duty = get_on_duty(abbrev)

# slack authentication & message posting
client = WebClient(token='xoxb-3882850848320-4839925368289-QxzrbFIC5jFiN344EZIxdNXk')

try:
    response = client.chat_postMessage(channel="C03RMNF8GC9", text=people_on_duty)
    # assert response["message"]["text"] == "drop dead"
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["ok"] is False
    # assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    print(f"Got an error: {e.response['error']}")

