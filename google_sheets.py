import gspread
from settings import CREDENTIALS, SHEET_ID

#Это ГЛАВНЫЙ ОБЪЕКТ API - получает доступ к документу, может открыть существующий документ, создать новый и т.д.
SERVICE = gspread.service_account_from_dict(CREDENTIALS) #Для инициализации сервиса (Google Sheets) из словаря, CREDENTIALS из файла settings

# Далее создадим константу SHEET - это будет сам документ. У объекта SERVICE есть функция open_by_key передаем в нее ID документа из его адресной строки, это SHEET_ID из файла settings
SHEET = SERVICE.open_by_key(SHEET_ID)

#Далее нам нужно получить WORKSHEET, т.е. лист документа. Создадим константу WORKSHEET, в которую передаем первый лист документа. Функция get_worksheet получает лист по индексу:
# 0 - это индекс первого листа документа
WORKSHEET = SHEET.get_worksheet(0)

def get_numeric_list(input_list): #Функция, которая преобразует все значения по колонке "Выручка" к числовым
    output_list = []             # В input_list будет подаваться values_list в функции get_total_revenue, см. ниже
    for i in input_list:
        try:
            output_list.append(float(i))
        except:
            pass
    return output_list

def get_total_revenue(): #Функция, которая считает сумму всех значений списка values_list - по колонке "Выручка"
    values_list = WORKSHEET.col_values(3, 'UNFORMATTED_VALUE') #передаёт в список значения по колонке "Выручка" с листа WORKSHEET
    # col_values - функция возвращает все данные из 3й колоки таблицы realty в Google Doc и включает в себя функцию get_numeric_list
    # параметр UNFORMATTED_VALUE значение будет вычислено как неотформатированное, т.к. считает все форматы (см.Ctrl+клик > описание с сылкой на документацию), преобразовав все значения к числовому типу.
    return sum(get_numeric_list(values_list)) #суммирует преобразованные в числа функцией get_numeric_list значения списка

def add_row(values_list): #функция по добавлению данных в Google Doc
    WORKSHEET.insert_row(values_list, 2)
