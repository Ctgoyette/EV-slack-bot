from datetime import datetime, timedelta
import gspread

from slack_sdk import WebClient;
from slack_sdk.errors import SlackApiError;

# call google spreadsheet
gc = gspread.service_account(filename=r'ev-slack-bot-credentials.json')
sheet = gc.open('EVH Spring 2024 Duty + More (27)')
duty_worksheet = sheet.worksheet('Duty')
try:
    move_out_worksheet = sheet.worksheet('Move-Out')
except:
    move_out_worksheet = None
try:
    move_in_worksheet = sheet.worksheet('Move-In By Shift')
except:
    move_in_worksheet = None

    
# finds the people on duty for the given date
def get_people_on_row(worksheet, row, start_column):
    try:
        start_column -= 1
        list_of_people = []
        current_row_values = worksheet.row_values(row)
        current_row_values.append('')
        name = current_row_values[start_column]
        while name is not None and name != '':
            list_of_people.append(name)
            start_column += 1
            name = current_row_values[start_column]
        people_list_length = len(list_of_people)
        people_string = list_of_people[0]
        if people_list_length == 1:
            pass
        elif people_list_length == 2:
            people_string = list_of_people[0] + ' & ' + list_of_people[1]
        else:
            for person in list_of_people[1:]:
                if person == list_of_people[-1]:
                    people_string = people_string + ', & ' + person
                else:
                    people_string = people_string + ', ' + person
        return(people_string)
    except Exception as e:
        print(e)
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
        print (move_out_worksheet.row_count)
        print('Could not find any move-out shifts for today')
        return None
    
def get_move_in(date):
    DATE_COLUMN = 1
    TIME_COLUMN = 3
    FIRST_RA_COLUMN = 5
    try:
        target_row = move_in_worksheet.find(date).row
        move_in_row = get_people_on_row(move_in_worksheet, target_row, FIRST_RA_COLUMN)
        move_in_people = '`' + move_in_worksheet.cell(target_row, TIME_COLUMN).value + '`: ' + move_in_row
        target_row += 1
        while (target_row - 1 != move_in_worksheet.row_count) and (move_in_worksheet.cell(target_row, FIRST_RA_COLUMN).value is not None) and (move_in_worksheet.cell(target_row, DATE_COLUMN).value is None):
            move_in_row = get_people_on_row(move_in_worksheet, target_row, FIRST_RA_COLUMN)
            move_in_people = move_in_people + '\n' + '`' + move_in_worksheet.cell(target_row, TIME_COLUMN).value + '`: ' + move_in_row
            target_row +=1
        return(move_in_people)
    except Exception as e:
        print(e)
        print("Move in worksheet rows: {}".format(move_in_worksheet.row_count))
        print('Could not find any move-in shifts for today')
        return None
    

today = datetime.now() + timedelta(days=9)
display_formatted_date = today.strftime('%B %d, %Y')
abbrev_duty_date = today.strftime('%b %d').replace(' 0', ' ')
abbrev_move_out_date = today.strftime('%m/%d').replace(' 0', ' ')
abbrev_move_in_date = today.strftime('%a %b %d').replace(' 0', ' ')
people_on_duty = get_on_duty(abbrev_duty_date)
try:
    move_out_people = get_move_out(abbrev_move_out_date)
except:
    move_out_people = None
try:
    move_in_people = get_move_in(abbrev_move_in_date)
except Exception as er:
    print(er)
    move_in_people = None


duty_text = display_formatted_date + "\n"
if move_out_people is not None:
    duty_text += "*Duty:*\n" + people_on_duty + "\n\n*Move Out Shifts:*\n" + move_out_people
elif move_in_people is not None:
    duty_text += "*Duty:*\n" + people_on_duty + "\n\n*Move In Shifts:*\n" + move_in_people
else:
    duty_text += people_on_duty


# slack authentication & message posting
slack_creds_file = open("ev-slack-app-auth.txt", "r")
client = WebClient(token=slack_creds_file.readline())
try:
    response = client.chat_postMessage(channel='C069GEG60G3', text=duty_text) # Bot channel
    #response = client.chat_postMessage(channel='C05CDGPHMU2', text=duty_text) # Duty info channel
    # assert response["message"]["text"] == "drop dead"
    print(duty_text)
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["ok"] is False
    # assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    print(f"Got an error: {e.response['error']}")






