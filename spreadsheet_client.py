from datetime import datetime, timedelta
import gspread

class SpreadsheetClient:
    def __init__(self, creds_file, sheets_file, duty_worksheet = None, move_in_worksheet = None, move_out_worksheet=None):
        self.account = gspread.service_account(filename=creds_file)
        self.spreadsheet_file = self.account.open(sheets_file)
        try:
            self.duty_worksheet = self.spreadsheet_file.worksheet(duty_worksheet)
        except:
            self.duty_worksheet = None
        try:
            self.move_in_worksheet = self.spreadsheet_file.worksheet(
                move_in_worksheet)
        except:
            self.move_in_worksheet = None
        try:
            self.move_out_worksheet = self.spreadsheet_file.worksheet(
                move_out_worksheet)
        except:
            self.move_out_worksheet = None

    def get_people_on_row(self, worksheet, row, start_column, account_for_blank = -1):
        try:
            start_column -= 1
            list_of_people = []
            current_row_values = worksheet.row_values(row)
            current_row_values.append('/0')
            name = ''
            name = current_row_values[start_column]
            if account_for_blank == -1:
                while name is not None and name != '/0':
                    list_of_people.append(name)
                    start_column += 1
                    name = current_row_values[start_column]
            else:
                while (start_column < (account_for_blank)) and (name != '/0'):
                    if (name is not None) and name != '':
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
            return (people_string)
        except Exception as e:
            print(e)
            print("Could not get people in the row")

    def get_on_duty(self, date):
        try:
            target_row = self.duty_worksheet.find(date).row
            duty_people = self.get_people_on_row(
                self.duty_worksheet, target_row, 6)
            return (duty_people)
        except:
            return ("Happy Holidays!")

    def get_move_out(self, date):
        DATE_COLUMN = 1
        TIME_COLUMN = 3
        FIRST_RA_COLUMN = 5
        try:
            target_row = self.move_out_worksheet.find(date).row
            move_out_row = self.get_people_on_row(
                self.move_out_worksheet, target_row, FIRST_RA_COLUMN)
            move_out_people = self.move_out_worksheet.cell(
                target_row, TIME_COLUMN).value + ': ' + move_out_row
            target_row += 1
            while (target_row - 1 != self.move_out_worksheet.row_count) and (self.move_out_worksheet.cell(target_row, FIRST_RA_COLUMN).value is not None) and (self.move_out_worksheet.cell(target_row, DATE_COLUMN).value is None):
                move_out_row = self.get_people_on_row(
                    self.move_out_worksheet, target_row, FIRST_RA_COLUMN)
                move_out_people = move_out_people + '\n' + \
                    self.move_out_worksheet.cell(
                        target_row, TIME_COLUMN).value + ': ' + move_out_row
                target_row += 1
            return (move_out_people)
        except Exception as e:
            print(self.move_out_worksheet.row_count)
            print('Could not find any move-out shifts for today')
            return None

    def get_move_in(self, date):
        DATE_COLUMN = 1
        TIME_COLUMN = 3
        FIRST_RA_COLUMN = 5
        LAST_RA_COLUMN = 15
        try:
            target_row = self.move_in_worksheet.find(date).row
            move_in_row = self.get_people_on_row(
                self.move_in_worksheet, target_row, FIRST_RA_COLUMN, LAST_RA_COLUMN)
            move_in_people = '`' + \
                self.move_in_worksheet.cell(
                    target_row, TIME_COLUMN).value + ':` ' + move_in_row
            target_row += 1
            while (target_row - 1 != self.move_in_worksheet.row_count) and (self.move_in_worksheet.cell(target_row, FIRST_RA_COLUMN).value is not None) and (self.move_in_worksheet.cell(target_row, DATE_COLUMN).value is None):
                move_in_row = self.get_people_on_row(
                    self.move_in_worksheet, target_row, FIRST_RA_COLUMN, LAST_RA_COLUMN)
                move_in_people = move_in_people + '\n' + '`' + \
                    self.move_in_worksheet.cell(
                        target_row, TIME_COLUMN).value + ':` ' + move_in_row
                target_row += 1
            return (move_in_people)
        except Exception as e:
            print(e)
            print("Move in worksheet rows: {}".format(
                self.move_in_worksheet.row_count))
            print('Could not find any move-in shifts for today')
            return None
