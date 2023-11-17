import base64
import hashlib
import hmac
import json
from datetime import datetime
from functools import wraps

import telebot
from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse

import app.telegram_service as telegram_service
from app import app, db, scheduler
from app.models import Connection, LinkType, PaymentType, User
from app.service import (add_fixed_payment, add_spending, connect_link,
                         create_user, get_connection_types, get_connections,
                         get_records, remove_fixed_payments, remove_spendings)
from app.telegram_function import get_column, get_row
from app.utils import string_generator

bot = telebot.TeleBot(app.config["BOT_TOKEN"])
webhook_url = 'https://8020-42-112-223-136.ngrok-free.app/webhook'
bot.set_webhook(url=webhook_url)


def with_app_context(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        with app.app_context():
            return f(*args, **kwargs)
    return decorated
# ------------------------------- SCHEDULER ---------------------------------
@scheduler.task('cron', id='do_job_1', day='*')
@with_app_context
def notification():
    connections = set(Connection.query.filter_by(connect_type=LinkType.GGSHEET.value).all())
    for connection in connections:
        data = get_column(connection.connect_link, "Monthly Payment", 3)
        if data[0] != "Day Payment":
            continue
        data = data[1:]
        current_date = datetime.now().strftime('%d')
        for i,date in enumerate(data):
            if date == current_date:
                res = get_row(connection.connect_link, "Monthly Payment", i+2)
                if int(res[1]) > 0:
                    continue
                user = User.query.filter_by(id=connection.user_id).first()
                if user is None:
                    continue
                amount = abs(int(res[1]))
                send_message(user.id, "Today is the day you have to pay {} VND for {}".format(amount,res[0]))

# --------------------------------- TELEGRAM BOT --------------------------------

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(
        request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return '', 200
def send_message(user_id, message):
    bot.send_message(user_id, message)
@bot.message_handler(commands=['get_link'])
@with_app_context
def tl_get_url(message):
    telegram_service.handle_get_url(bot, message)

@bot.message_handler(commands=['income'])
@with_app_context
def tl_income(message):
    telegram_service.add(bot, message,1)
    
@bot.message_handler(commands=['expense'])
@with_app_context
def tl_expense(message):
    telegram_service.add(bot, message,-1)
    
@bot.message_handler(commands=['remove'])
@with_app_context
def tl_remove(message):
    telegram_service.remove_spending(bot, message)
    
@bot.message_handler(commands=['get'])
@with_app_context
def tl_get(message):
    telegram_service.get_record(bot, message)
    
@bot.message_handler(commands=['statistic'])
@with_app_context
def tl_statistic(message):
	telegram_service.get_statistic(bot, message)
    
@bot.message_handler(commands=['income_monthly'])
@with_app_context
def tl_income_monthly(message):
	telegram_service.add_monthly(bot, message,1)

@bot.message_handler(commands=['expense_monthly'])
@with_app_context
def tl_expense_monthly(message):
	telegram_service.add_monthly(bot, message,-1)

@bot.message_handler(commands=['remove_monthly'])
@with_app_context
def tl_remove_monthly(message):
	telegram_service.remove_monthly(bot, message)
    
@bot.message_handler(commands=['get_monthly'])
@with_app_context
def tl_get_monthly(message):
	telegram_service.get_record(bot, message,"Monthly Payment")
@bot.message_handler(commands=['link'])
@with_app_context
def tl_set_link(message):
	telegram_service.set_link(bot, message)
# ------------------------------- FLASK ROUTES ---------------------------------
@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html', user=current_user)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user, payment_types=PaymentType)


@app.route('/monthly-payment')
@login_required
def monthly_payment_func():
    return render_template('monthlyPayment.html', user=current_user, payment_types=PaymentType)


@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    data = {'bot_name': app.config["BOT_USER_NAME"],
            'bot_domain': app.config["URL"]}
    return render_template('login.html', data=data, user=current_user)


@app.route('/login-telegram')
def login_telegram():
    tg_data = {
        "id": request.args.get('id', None),
        "first_name": request.args.get('first_name', None),
        "last_name": request.args.get('last_name', None),
        "username": request.args.get('username', None),
        "photo_url": request.args.get('photo_url', None),
        "auth_date":  request.args.get('auth_date', None),
        "hash": request.args.get('hash', None)
    }
    data_check_string = string_generator(tg_data)
    secret_key = hashlib.sha256(
        app.config['BOT_TOKEN'].encode('utf-8')).digest()
    secret_key_bytes = secret_key
    data_check_string_bytes = bytes(data_check_string, 'utf-8')
    hmac_string = hmac.new(
        secret_key_bytes, data_check_string_bytes, hashlib.sha256).hexdigest()
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
    return render_template('profile.html', user=current_user, connection_types=get_connection_types(),
                           connections=get_connections(current_user.id))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/connect', methods=['GET', 'POST'])
@login_required
def connect():
    if request.method == 'POST':
        connect_link(
            current_user.id, request.form['connect_type'], request.form['connect_link'])
    return redirect(url_for('profile'))


@app.route('/add', methods=['POST'])
@login_required
def add():
    if request.method == 'POST':
        name = request.form['name']
        amount = request.form['amount']
        typee = request.form['type']
        desc = request.form['desc']
        type_payment = int(request.form['payment_type'])
        if type_payment == PaymentType.INCOME.value:
            amount = int(amount)
        else:
            amount = -int(amount)
        print(type_payment == PaymentType.INCOME.value)
        add_spending(current_user.id, name, amount, typee, desc)
        flash('Add {} success'.format(name))
    return redirect(url_for('dashboard'))


@app.route('/remove', methods=['POST'])
@login_required
def remove():
    if request.method == 'POST':
        row = request.form['row_index']
        remove_spendings(current_user.id, json.loads(row))
        return ('Remove row {} success'.format(json.loads(row)))
    return None


@app.route("/remove-fixed-payment", methods=['POST'])
@login_required
def remove_fixed_payment():
    if request.method == 'POST':
        row = request.form['row_index']
        remove_fixed_payments(current_user.id, json.loads(row))
        return ('Remove row {} success'.format(json.loads(row)))
    return None


@app.route('/add-monthly', methods=['POST'])
@login_required
def add_fixed():
    if request.method == 'POST':
        name = request.form['name']
        amount = request.form['amount']
        day_payment = request.form['day_payment']
        desc = request.form['desc']
        type_payment = int(request.form['payment_type'])
        if type_payment == PaymentType.INCOME.value:
            amount = int(amount)
        else:
            amount = -int(amount)
        print(type_payment == PaymentType.INCOME.value)
        add_fixed_payment(current_user.id, name, amount, day_payment, desc)
        flash('Add {} success'.format(name))
    return redirect(url_for('monthly_payment_func'))


@app.route('/records')
@login_required
def records():
    records = get_records(current_user.id, request.args.get('time'))
    return jsonify(records)


@app.route('/monthly-records')
@login_required
def monthly_records():
    records = get_records(current_user.id, "Monthly Payment")
    return jsonify(records)
# template filters


@app.template_filter('timestamp_to_datetime')
def timestamp_to_datetime(value):
    value = int(value)
    return datetime.fromtimestamp(value).strftime('%Y-%m-%d')
