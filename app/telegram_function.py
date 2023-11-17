import re

import gspread
from gspread.exceptions import WorksheetNotFound

from app.utils import add_index, convert_array_to_dict

gc = gspread.service_account(filename='credentials.json')
def get_sheet(url:str, sheet_name:str):
    sh = gc.open_by_url(url)
    worksheet = sh.worksheet(sheet_name)
    return worksheet.get_all_records()

def get_last_record(url:str, sheet_name:str,number_of_record:int):
    all_record = get_sheet(url, sheet_name)
    num = len(all_record)
    if num < number_of_record:
        return all_record,num
    return all_record[-number_of_record:],len(all_record)
def check_sheet(url:str, sheet_name:str):
    try:
        sh = gc.open_by_url(url)
        worksheet = sh.worksheet(sheet_name)
        return True
    except WorksheetNotFound as e:
        return False
def create_sheet(url:str, sheet_name:str):
    try:
        if(not check_sheet(url, "Monthly Payment")):
            create_sheet_mothly(url)
        sh = gc.open_by_url(url)
        sh.add_worksheet(title=sheet_name, rows="100", cols="20")
        worksheet = sh.worksheet(sheet_name)
        worksheet.append_row(["Name", "Amount", "Type", "Time", "Description"])
        worksheet.update_acell("G1", "Total Amount")
        worksheet.update_acell("G2", "=SUM($B$2:B)+'Monthly Payment'!$G$2")
        return True
    except Exception as e:
        return False
def create_sheet_mothly(url:str):
    try:
        sh = gc.open_by_url(url)
        sh.add_worksheet(title="Monthly Payment", rows="100", cols="20")
        worksheet = sh.worksheet("Monthly Payment")
        worksheet.append_row(["Name", "Amount", "Day Payment", "Description"])
        worksheet.update_acell("G1", "Total Amount")
        worksheet.update_acell("G2", "=sum($B$2:B)")
        return True
    except Exception as e:
        return False
def add_monthly_payment(url:str, data):
    try:
        sh = gc.open_by_url(url)
        worksheet = sh.worksheet("Monthly Payment")
        return get_table_range_info(worksheet.append_row(values=data,table_range="A1").get('updates').get("updatedRange"))
    except WorksheetNotFound as e:
        create_sheet_mothly(url)
        add_monthly_payment(url, data)
    except Exception as e:
        return
    
def get_table_range_info(table_range:str):
    match = re.match(r"'([^']+)'!([A-Z]\d+:[A-Z]\d+)", table_range)
    if match:
        sheet_name = match.group(1)  # Lấy tên sheet
        cell_range = match.group(2)  # Lấy dải ô
        # Tách dải ô thành cặp tên cột và số dòng
        start_cell, end_cell = cell_range.split(':')
        return {"sheet_name":sheet_name, "start_cell":start_cell, "end_cell":end_cell}
    else:
        print("Không tìm thấy thông tin hợp lệ.")

def append_sheet(url:str, sheet_name:str,data,table_range="A1"):
    try:
        sh = gc.open_by_url(url)
        worksheet = sh.worksheet(sheet_name)
        res = worksheet.append_row(values=data,table_range=table_range)
        return get_table_range_info(res.get('updates').get("updatedRange"))
    except WorksheetNotFound as e:
        create_sheet(url, sheet_name)
        append_sheet(url, sheet_name, data)
    except Exception as e:
        return 
    

def get_sheet(url:str, sheet_name:str,range:str="A1:E"):
    try:
        sh = gc.open_by_url(url)
        worksheet = sh.worksheet(sheet_name)
        data = worksheet.get_values(range)
        return add_index(convert_array_to_dict(data),2)
    except WorksheetNotFound as e:
        return False
    except Exception as e:
        return
def get_last_record(url:str, sheet_name:str,number_of_record:int):
    try:
        all_record = get_sheet(url, sheet_name)
        return all_record[-number_of_record:],len(all_record)
    except Exception as e:
        return
def delete_row(url:str, sheet_name:str, row_index:int):
    try:
        sh = gc.open_by_url(url)
        worksheet = sh.worksheet(sheet_name)
        return worksheet.delete_rows(row_index)
    except Exception as e:
        print(e)
        return
def delete_rows(url:str, sheet_name:str, row_indexes:list):
    try:
        sh = gc.open_by_url(url)
        worksheet = sh.worksheet(sheet_name)
        sorted_row_indexes = sorted(row_indexes, reverse=True)
        for row_index in sorted_row_indexes:
            worksheet.delete_rows(row_index)
        return True
    except Exception as e:
        print(e)
        return
def update_cell(url:str, sheet_name:str, cell:str, value:str):
    try:
        sh = gc.open_by_url(url)
        worksheet = sh.worksheet(sheet_name)
        worksheet.update_acell(cell, value)
    except Exception as e:
        print(e)
        return
def get_total_amount(url:str,sheet_name:str):
    try:
        sh = gc.open_by_url(url)
        worksheet = sh.worksheet(sheet_name)
        return worksheet.acell("G2").value
    except Exception as e:
        print(e)
        return
def get_column(url, sheet_name, column:int):
    try:
        sh = gc.open_by_url(url)
        worksheet = sh.worksheet(sheet_name)
        return worksheet.col_values(column)
    except Exception as e:
        print(e)
        return []
    
def get_row(url, sheet_name, row:int):
    try:
        sh = gc.open_by_url(url)
        worksheet = sh.worksheet(sheet_name)
        return worksheet.row_values(row)
    except Exception as e:
        print(e)
        return []