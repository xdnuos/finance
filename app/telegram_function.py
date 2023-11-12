import re

import gspread
from gspread.exceptions import WorksheetNotFound

from app.utils import add_index

gc = gspread.service_account(filename='credentials.json')
def create_sheet(url:str, sheet_name:str):
    try:
        sh = gc.open_by_url(url)
        sh.add_worksheet(title=sheet_name, rows="100", cols="20")
        sh.append_row(["Name", "Amount", "Type", "Time", "Description"])
        return True
    except Exception as e:
        return False
def get_table_range_info(table_range:str):
    match = re.match(r"'(\d+/\d+)'!([A-Z]\d+:[A-Z]\d+)", table_range)
    if match:
        sheet_name = match.group(1)  # Lấy tên sheet
        cell_range = match.group(2)  # Lấy dải ô
        # Tách dải ô thành cặp tên cột và số dòng
        start_cell, end_cell = cell_range.split(':')
        return {"sheet_name":sheet_name, "start_cell":start_cell, "end_cell":end_cell}
    else:
        print("Không tìm thấy thông tin hợp lệ.")

def append_sheet(url:str, sheet_name:str,data):
    try:
        sh = gc.open_by_url(url)
        worksheet = sh.worksheet(sheet_name)
        return get_table_range_info(worksheet.append_row(data).get('updates').get("updatedRange"))
    except WorksheetNotFound as e:
        create_sheet(url, sheet_name)
        append_sheet(url, sheet_name, data)
    except Exception as e:
        return 
    

def get_sheet(url:str, sheet_name:str):
    try:
        sh = gc.open_by_url(url)
        worksheet = sh.worksheet(sheet_name)
        return add_index(worksheet.get_all_records(),2)
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