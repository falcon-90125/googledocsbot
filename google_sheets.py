import gspread
from settings import CREDENTIALS

SERVICE = gspread.service_account_from_dict(CREDENTIALS)
SHEET = SERVICE.open_by_key('1TYWxZ93ZLmrXAvAgFXdg1XMR-DmQ212hENJVYHwrbdY')
WORKSHEET = SHEET.get_worksheet(0)

values_list = [1, 'abc', 3]
def get_numeric_list(input_list):
    output_list = []
    for i in input_list:
        try:
            output_list.append(float(i))
        except:
            pass
    return output_list

def get_total_revenue():
    values_list = WORKSHEET.col_values(3, 'UNFORMATTED_VALUE')
    return sum(get_numeric_list(values_list))

print(get_total_revenue())
