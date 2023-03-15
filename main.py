from datetime import datetime
from google_sheets_integration import Sheet

today = datetime.now()

abbrev = today.strftime('%b %d').replace(' 0', ' ')

duty_sheet = Sheet()
people_on_duty = duty_sheet.get_on_duty(abbrev)
print(people_on_duty)


