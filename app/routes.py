import base64
import hashlib
import hmac
import json
from datetime import datetime

from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse

from app import app, db
from app.service import (add_spending, connect_link, create_user,
                         get_connection_types, get_connections, get_records,
                         remove_spendings)
from app.utils import string_generator


@app.route('/')
@app.route('/index')
def index():
	if current_user.is_authenticated:
		return redirect(url_for('dashboard'))
	return render_template('index.html',user=current_user)

@app.route('/dashboard')
@login_required
def dashboard():

	return render_template('dashboard.html',user=current_user)
@app.route('/login')
def login():
	if current_user.is_authenticated:
		return redirect(url_for('dashboard'))
	data = {'bot_name': app.config["BOT_USER_NAME"], 'bot_domain': app.config["URL"]}
	return render_template('login.html',data = data,user=current_user)
@app.route('/login-telegram')
def login_telegram():
	tg_data = {
		"id" : request.args.get('id',None),
		"first_name" : request.args.get('first_name',None),
		"last_name" : request.args.get('last_name', None),
		"username" : request.args.get('username', None),
		"photo_url": request.args.get('photo_url', None),
		"auth_date":  request.args.get('auth_date', None),
		"hash" : request.args.get('hash',None)
	}
	data_check_string = string_generator(tg_data)
	secret_key = hashlib.sha256(app.config['BOT_TOKEN'].encode('utf-8')).digest()
	secret_key_bytes = secret_key
	data_check_string_bytes = bytes(data_check_string,'utf-8')
	hmac_string = hmac.new(secret_key_bytes, data_check_string_bytes, hashlib.sha256).hexdigest()
	if hmac_string == tg_data['hash']:
		login_user(create_user(tg_data))
		return redirect(url_for('dashboard'))
	
	return jsonify({
				'hmac_string': hmac_string,
				'tg_hash': tg_data['hash'],
				'tg_data': tg_data
	})

@app.route('/profile')
@login_required
def profile():
	return render_template('profile.html', user=current_user,connection_types=get_connection_types(),
						connections = get_connections(current_user.id))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/connect', methods=['GET', 'POST'])
@login_required
def connect():
	if request.method == 'POST':
		connect_link(current_user.id,request.form['connect_type'],request.form['connect_link'])
	return redirect(url_for('profile'))

@app.route('/add', methods=['POST'])
@login_required
def add():
	if request.method == 'POST':
		name = request.form['name']
		amount = request.form['amount']
		type = request.form['type']
		desc = request.form['desc']
		add_spending(current_user.id,name,amount,type,desc)
	flash('Add {} success'.format(name))
	return redirect(url_for('dashboard'))

@app.route('/remove', methods=['POST'])
@login_required
def remove():
	if request.method == 'POST':
		row = request.form['row_index']
		remove_spendings(current_user.id,json.loads(row))
	return 'Remove row {} success'.format(json.loads(row))

@app.route('/records')
@login_required
def records():
	records = get_records(current_user.id,request.args.get('time'))
	return jsonify(records)
# template filters
@app.template_filter('timestamp_to_datetime')
def timestamp_to_datetime(value):
	value = int(value)
	return datetime.fromtimestamp(value).strftime('%Y-%m-%d')

	
