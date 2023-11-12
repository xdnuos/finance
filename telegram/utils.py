import datetime
from itertools import chain
from itertools import zip_longest as izip_longest

import gspread
import requests
from tabulate import tabulate
from telebot.types import Message

gc = gspread.service_account(filename='credentials.json')
import re


def convert_dict_to_list(rows):
    uniq_keys = set()  # implements hashed lookup
    keys = []  # storage for set
    for row in rows:
        for k in row.keys():
            # Save unique items in input order
            if k not in uniq_keys:
                keys.append(k)
                uniq_keys.add(k)
    return [[row.get(k) for k in keys] for row in rows]
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

def write_to_sheet(url:str, sheet_name:str,data):
    sh = gc.open_by_url(url)
    worksheet = sh.worksheet(sheet_name)
    worksheet.append_row(data)
    return get_table_range_info(worksheet.append_row(data).get('updates').get("updatedRange"))

def get_sheet(url:str, sheet_name:str):
    sh = gc.open_by_url(url)
    worksheet = sh.worksheet(sheet_name)
    return worksheet.get_all_records()
def get_last_record(url:str, sheet_name:str,number_of_record:int):
    all_record = get_sheet(url, sheet_name)
    return all_record[-number_of_record:],len(all_record)
def delete_row(url:str, sheet_name:str, row_index:int):
    sh = gc.open_by_url(url)
    worksheet = sh.worksheet(sheet_name)
    return worksheet.delete_rows(row_index)
def add(bot, message: Message):
    try:
        amount = int(re.search(r'/add\s+(\d+)', message.text).group(1)) * 1000
        name = re.search(r'/add\s+\d+\s+(.*)', message.text).group(1)
        date = datetime.datetime.now().strftime("%m/%d/%Y")
        sheet_name = "{}/{}".format(datetime.datetime.now().month, datetime.datetime.now().year)
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "Sorry, I didn't understand that kind of message")
        return
    url = "https://docs.google.com/spreadsheets/d/1FfZOET9rwsTFiSINmbacgC-XabNOt0XSS9v6kIyi8wA/edit#gid=1069132846"
    data = [name, amount , date]
    r = write_to_sheet(url, sheet_name, data)
    try:
        bot.send_message(message.chat.id, f"Add {data[0]} to sheet {r['sheet_name']} at line {r['start_cell'][1:]}")
    except Exception as e:
        print(e)  # for DEBUG purpose
def remove(bot, message:Message):
    try:
        row_index = int(re.search(r'/remove\s+(\d+)', message.text).group(1))
        sheet_name = "{}/{}".format(datetime.datetime.now().month, datetime.datetime.now().year)
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "Sorry, I didn't understand that kind of message")
        return
    url = "https://docs.google.com/spreadsheets/d/1FfZOET9rwsTFiSINmbacgC-XabNOt0XSS9v6kIyi8wA/edit#gid=1069132846"
    r = delete_row(url, sheet_name, row_index)
    try:
        bot.send_message(message.chat.id, f"Remove line {row_index} from sheet {sheet_name}")
    except Exception as e:
        print(e)  # for DEBUG purpose
    print(row_index)  # for DEBUG purpose
def get_record(bot, message:Message):
    try:
        sheet_name = "{}/{}".format(datetime.datetime.now().month, datetime.datetime.now().year)
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "Sorry, I didn't understand that kind of message")
        return
    url = "https://docs.google.com/spreadsheets/d/1FfZOET9rwsTFiSINmbacgC-XabNOt0XSS9v6kIyi8wA/edit#gid=1069132846"
    data,len_all = get_last_record(url, sheet_name,10)
    custom_indices = range(len_all-8, len_all+2)
    # Chuyển đổi dữ liệu thành bảng sử dụng tabulate
    table = tabulate(convert_dict_to_list(data), headers=["Row","Name", "Amount","Time"],tablefmt="simple", 
                     showindex=custom_indices, colalign=("left", "left", "right", "right"),maxcolwidths=[3, 12, None,None])
    try:
        
        bot.send_message(message.chat.id,"```"+"#Last10Records\n"+table + "```", parse_mode="MarkdownV2")
    except Exception as e:
        print(e)  # for DEBUG purpose
def get_sum(bot,message:Message):
    try:
        sheet_name = "{}/{}".format(datetime.datetime.now().month, datetime.datetime.now().year)
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "Sorry, I didn't understand that kind of message")
        return
    url = "https://docs.google.com/spreadsheets/d/1FfZOET9rwsTFiSINmbacgC-XabNOt0XSS9v6kIyi8wA/edit#gid=1069132846"
    data,len_all = get_last_record(url, sheet_name,10)
    custom_indices = range(len_all-8, len_all+2)
    # Chuyển đổi dữ liệu thành bảng sử dụng tabulate
    table = tabulate(convert_dict_to_list(data), headers=["Row","Name", "Amount","Time"],tablefmt="simple", 
                     showindex=custom_indices, colalign=("left", "left", "right", "right"),maxcolwidths=[3, 12, None,None])
    try:
        
        bot.send_message(message.chat.id,"```"+"#Last10Records\n"+table + "```", parse_mode="MarkdownV2")
    except Exception as e:
        print(e)  # for DEBUG purpose
if __name__ == '__main__':
    url = "https://docs.google.com/spreadsheets/d/1FfZOET9rwsTFiSINmbacgC-XabNOt0XSS9v6kIyi8wA/edit#gid=1069132846"
    # print(write_to_sheet(url, "11/2023", ["test2", 1000, "1/1/2021"]).get("start_cell")[1:])
    data,len_all = get_last_record(url, "11/2023", 10)
    custom_indices = range(len_all-8, len_all+2)
    data = convert_dict_to_list(data)
    table = tabulate(data, headers=["Row","Name", "Amount","Time"],tablefmt="rounded_grid", 
                     showindex=custom_indices, colalign=("left", "left", "right", "right"),maxcolwidths=[3, 9, None,None])
    print(table)
