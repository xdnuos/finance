import datetime
import re

import gspread
from tabulate import tabulate
from telebot.types import Message

import app.telegram_function as telegram_function
import app.utils as utils
from app.models import Connection, LinkType
from app.service import connect_link, get_link


def set_link(bot, message: Message):
    try:
        url = re.search(r'/link\s+(.*)', message.text).group(1)
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "Sorry, I didn't understand that kind of message")
        return
    user_id = message.from_user.id
    try:
        connection = Connection.query.filter_by(user_id=user_id, connect_type=LinkType.GGSHEET.value).first()
        if connection is None:
            connect_link(user_id, LinkType.GGSHEET.value, url)
            bot.send_message(message.chat.id, "Set url successfully")
        else:
            connection.connect_link = url
            try:
                connection.save()
                bot.send_message(message.chat.id, "Change url successfully")
            except Exception as e:
                print(e)
                bot.send_message(message.chat.id, "An error occurred. Please try again later")
                return
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "An error occurred. Please try again later")
        return
def handle_get_url(bot, message: Message):
    user_id = message.from_user.id
    link = get_link(user_id,LinkType.GGSHEET.value)
    if link is None:
        bot.send_message(message.chat.id, "You haven't connected to any sheet yet")
    else:
        bot.send_message(message.chat.id, link)
def add(bot, message: Message,value):
    if value == 1:
        command = r'/income\s+([^,]+),\s*([^,]+)(?:,\s*([^,]+))?(?:,\s*(.*))?$'
    else:
        command = r'/expense\s+([^,]+),\s*([^,]+)(?:,\s*([^,]+))?(?:,\s*(.*))?$'
    try:
        match = re.search(command, message.text)
        if match is None:
            bot.send_message(message.chat.id, "Sorry, I didn't understand that kind of message")
    except Exception as e:
        # Nếu không có kết quả từ biểu thức chính quy
        bot.send_message(message.chat.id, "Sorry, I didn't understand that kind of message")
        print(e)
        return
    name = match.group(1)
    amount = int(match.group(2))*value
    expense_type = match.group(3)
    desc = match.group(4)
    time = datetime.datetime.now().strftime("%m/%d/%Y")
    sheet_name = "{}/{}".format(datetime.datetime.now().month, datetime.datetime.now().year)
    url = get_link(message.from_user.id,LinkType.GGSHEET.value)
    data = [name, amount ,expense_type, time,desc]
    r = telegram_function.append_sheet(url, sheet_name, data)
    try:
        bot.send_message(message.chat.id, f"Add {data[0]} to sheet {r['sheet_name']} at line {r['start_cell'][1:]}")
    except Exception as e:
        print(e)  # for DEBUG purpose
def remove_spending(bot, message:Message):
    try:
        row_index = int(re.search(r'/remove\s+(\d+)', message.text).group(1))
        sheet_name = "{}/{}".format(datetime.datetime.now().month, datetime.datetime.now().year)
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "Sorry, I didn't understand that kind of message")
        return
    url = get_link(message.from_user.id,LinkType.GGSHEET.value)
    telegram_function.delete_row(url, sheet_name, row_index)
    try:
        bot.send_message(message.chat.id, f"Remove line {row_index} from sheet {sheet_name}")
    except Exception as e:
        print(e)  # for DEBUG purpose
    print(row_index)  # for DEBUG purpose
def get_record(bot, message:Message,sheet_name=None):
    try:
        key = ["Index","Name", "Amount","Day Payment"]
        header = ["Row","Name","Amount","Day Payment"]
        if sheet_name is None:
            sheet_name = "{}/{}".format(datetime.datetime.now().month, datetime.datetime.now().year)
            key = ["Index","Name", "Amount","Time"]
            header = ["Row","Name","Amount","Time"]
        url = get_link(message.from_user.id,LinkType.GGSHEET.value)
        data,len_all = telegram_function.get_last_record(url, sheet_name,10)

        # Chuyển đổi dữ liệu thành bảng sử dụng tabulate
        table = tabulate(utils.convert_dict_to_list(data,key), headers=header,tablefmt="simple", 
                         colalign=("left", "left", "right", "right"),maxcolwidths=[3, 12, None,None])
        try:
            bot.send_message(message.chat.id,"```"+"#Last10Records\n"+table + "```", parse_mode="MarkdownV2")
        except Exception as e:
            print(e)  # for DEBUG purpose
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "An error occurred. Please try again later")
        return
def get_statistic(bot,message:Message):
    sheet_name = "{}/{}".format(datetime.datetime.now().month, datetime.datetime.now().year)
    url = get_link(message.from_user.id,LinkType.GGSHEET.value)
    data = telegram_function.get_sheet(url, sheet_name)
    for transaction in data:
        transaction['Amount'] = int(transaction['Amount'])

    # Lấy 5 giao dịch lớn nhất
    largest_transactions = sorted(data, key=lambda x: abs(x['Amount']), reverse=True)[:5]
    table = tabulate(utils.convert_dict_to_list(largest_transactions,["Name", "Amount","Time"]), headers=["Index","Name","Amount","Time"],tablefmt="simple", 
                    showindex=True, colalign=("left", "left", "right", "right"),maxcolwidths=[3, 12, None,None])
    # Tổng giao dịch âm
    negative_total = sum(transaction['Amount'] for transaction in data if transaction['Amount'] < 0)

    # Tổng giao dịch dương
    positive_total = sum(transaction['Amount'] for transaction in data if transaction['Amount'] > 0)
    try:
        bot.send_message(message.chat.id,"```"+"#Statistic\n"+"Total: {}\nIncome: {}\nExpense: {}\nLargest Transactions: \n{}\n```".format(positive_total + negative_total, positive_total, negative_total, table), parse_mode="MarkdownV2")
    except Exception as e:
        print(e)  # for DEBUG purpose

def add_monthly(bot, message: Message,value):
    if value == 1:
        command = r'/income_monthly\s+([^,]+),\s*([^,]+)(?:,\s*([^,]+))?(?:,\s*(.*))?$'
    else:
        command = r'/expense_monthly\s+([^,]+),\s*([^,]+)(?:,\s*([^,]+))?(?:,\s*(.*))?$'
    try:
        match = re.search(command, message.text)
        if match is None:
            bot.send_message(message.chat.id, "Sorry, I didn't understand that kind of message")
    except Exception as e:
        # Nếu không có kết quả từ biểu thức chính quy
        bot.send_message(message.chat.id, "Sorry, I didn't understand that kind of message")
        print(e)
        return
    name = match.group(1)
    amount = int(match.group(2))*value
    day_payment = match.group(3)
    desc = match.group(4)
    url = get_link(message.from_user.id,LinkType.GGSHEET.value)
    data = [name, amount ,day_payment,desc]
    r = telegram_function.append_sheet(url, "Monthly Payment", data)
    try:
        bot.send_message(message.chat.id, f"Add {data[0]} to sheet Monthly Payment at line {r['start_cell'][1:]}")
    except Exception as e:
        print(e)  # for DEBUG purpose
def remove_spending(bot, message:Message):
    try:
        row_index = int(re.search(r'/remove_monthly\s+(\d+)', message.text).group(1))
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "Sorry, I didn't understand that kind of message")
        return
    url = get_link(message.from_user.id,LinkType.GGSHEET.value)
    telegram_function.delete_row(url, "Monthly Payment", row_index)
    try:
        bot.send_message(message.chat.id, f"Remove line {row_index} from sheet Monthly Payment")
    except Exception as e:
        print(e)  # for DEBUG purpose
    print(row_index)  # for DEBUG purpose
def send_message(bot, message):
	bot.send_message()
