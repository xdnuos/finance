import json
from datetime import datetime

import telebot

from app import app, db
from app.models import Connection, ConnectType, LinkType, User
from app.telegram_function import (append_sheet, delete_row, delete_rows,
                                   get_sheet)
from app.utils import extract_values

bot = telebot.TeleBot(app.config["BOT_TOKEN"])
def create_user(tg_data):
	user = User.query.filter_by(id=tg_data['id']).first()
	if user is None:
		user = User(id=tg_data['id'],
			username=tg_data['username'],
			first_name=tg_data['first_name'],
			last_name=tg_data['last_name'],
			photo_url=tg_data['photo_url'],
			auth_date=tg_data['auth_date'])
		db.session.add(user)
		db.session.commit()
	return user
def connect_link(user_id,connect_type_id,link):
	if link is None:
		return False
	if user_id is None:
		return False
	if connect_type_id is None:
		return False
	user_id = int(user_id)
	connection = Connection(user_id=user_id,connect_type=connect_type_id,connect_link=link)
	db.session.add(connection)
	db.session.commit()
	return True
def get_connections(user_id):
	connections = Connection.query.filter_by(user_id=user_id).all()
	return connections
def get_connection_types():
	connection_types = ConnectType.query.all()
	return connection_types
def get_connection_type(connection_type_id):
	connection_type = ConnectType.query.filter_by(id=connection_type_id).first()
	return connection_type
def get_link(user_id,type):
	connection = Connection.query.filter_by(user_id=user_id,connect_type=type).first()
	if connection is None:
		return None
	return connection.connect_link
def add_spending(user_id,name,amount,type,desc,sheet_name=None):
	link = get_link(user_id,LinkType.GGSHEET.value)
	date = datetime.now().strftime("%m/%d/%Y")
	data = [name, amount,type,date,desc]
	if sheet_name is None:
		sheet_name = "{}/{}".format(datetime.now().month, datetime.now().year)
	append_sheet(link, sheet_name,data)
def remove_spending(user_id,row_index,sheet_name=None):
	link = get_link(user_id,LinkType.GGSHEET.value)
	if sheet_name is None:
		sheet_name = "{}/{}".format(datetime.now().month, datetime.now().year)
	row_index = int(row_index)
	delete_row(link, sheet_name,row_index)
def remove_spendings(user_id,row_indexes,sheet_name=None):
	link = get_link(user_id,LinkType.GGSHEET.value)
	if sheet_name is None:
		sheet_name = "{}/{}".format(datetime.now().month, datetime.now().year)
	delete_rows(link, sheet_name,extract_values(row_indexes, "id"))
def get_records(user_id,sheet_name=None):
	if sheet_name is None:
		sheet_name = "{}/{}".format(datetime.now().month, datetime.now().year)
	link = get_link(user_id,LinkType.GGSHEET.value)
	return get_sheet(link, sheet_name)