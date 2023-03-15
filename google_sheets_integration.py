import gspread

class Sheet:
    def __init__(self):
        self.gc = gspread.service_account(filename='../ev-slack-bot-credentials.json')
        self.sheet = self.gc.open('EVHMH RA Spring 2023 Duty + More')
        self.duty_worksheet = self.sheet.worksheet('Duty')
    
    def get_on_duty(self, date):
        try:
            target_row = self.duty_worksheet.find(date).row
            person_one = self.duty_worksheet.cell(target_row, 6).value
            person_two = self.duty_worksheet.cell(target_row, 7).value
            duty_string = '{} & {}'.format(person_one, person_two)
            return(duty_string)
        except:
            return("Looks like we have the day off! Jk, somebody should probabaly figure out who's on duty")
