from datetime import datetime, timedelta
import gspread

from slack_sdk import WebClient;
from slack_sdk.errors import SlackApiError;

# call google spreadsheet
gc = gspread.service_account(filename=r'ev-slack-bot-credentials.json')
sheet = gc.open('EVH RA Fall 2023 Duty + More')
duty_worksheet = sheet.worksheet('Duty')
try:
    move_out_worksheet = sheet.worksheet('Move-Out')
except:
    pass

    
# finds the people on duty for the given date
def get_people_on_row(worksheet, row, start_column):
    try:
        person_one = worksheet.cell(row, start_column).value
        person_two = worksheet.cell(row, start_column+1).value
        if person_two is not None:
            people_string = '{} & {}'.format(person_one, person_two)
        else:
            people_string = person_one
        return(people_string)
    except:
        print("Could not get people in the row")

def get_on_duty(date):
    try:
        target_row = duty_worksheet.find(date).row
        duty_people = get_people_on_row(duty_worksheet, target_row, 6)
        return(duty_people)
    except:
        return("Happy Holidays!")
    
def get_move_out(date):
    DATE_COLUMN = 2
    TIME_COLUMN = 3
    FIRST_RA_COLUMN = 4
    try:
        target_row = move_out_worksheet.find(date).row
        move_out_row = get_people_on_row(move_out_worksheet, target_row, FIRST_RA_COLUMN)
        move_out_people = move_out_worksheet.cell(target_row, TIME_COLUMN).value + ': ' + move_out_row
        target_row += 1
        while (target_row - 1 != move_out_worksheet.row_count) and (move_out_worksheet.cell(target_row, FIRST_RA_COLUMN).value is not None) and (move_out_worksheet.cell(target_row, DATE_COLUMN).value is None):
            move_out_row = get_people_on_row(move_out_worksheet, target_row, FIRST_RA_COLUMN)
            move_out_people = move_out_people + '\n' + move_out_worksheet.cell(target_row, TIME_COLUMN).value + ': ' + move_out_row
            target_row +=1
        return(move_out_people)
    except Exception as e:
        print (e)
        print (move_out_worksheet.row_count)
        print('Could not find any move-out shifts for today')
        return None
    

today = datetime.now()
abbrev_duty_date = today.strftime('%b %d').replace(' 0', ' ')
abbrev_move_out_date = today.strftime('%m/%d').replace(' 0', ' ')
people_on_duty = get_on_duty(abbrev_duty_date)
move_out_people = get_move_out(abbrev_move_out_date)
formatted_date = today.strftime('%B %d, %Y')



duty_text = formatted_date + "\n"
if move_out_people is not None:
    duty_text += "*Duty:*\n" + people_on_duty + "\n\n*Move Out Shifts:*\n" + move_out_people
else:
    duty_text += people_on_duty

# slack authentication & message posting
slack_creds_file = open("ev-slack-app-auth.txt", "r")
client = WebClient(token=slack_creds_file.readline())

try:
    response = client.chat_postMessage(channel='C05CDGPHMU2', text=duty_text) # Bot channel
    #response = client.chat_postMessage(channel='C05CDGPHMU2', text=duty_text) # Duty info channel
    # assert response["message"]["text"] == "drop dead"
    print(duty_text)
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["ok"] is False
    # assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    print(f"Got an error: {e.response['error']}")






