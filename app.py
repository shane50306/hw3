#!/usr/bin/env python3
# Foundations of Python Network Programming, Third Edition
# https://github.com/brandon-rhodes/fopnp/blob/m/py3/chapter11/app_insecure.py
# A poorly-written and profoundly insecure payments application.
# (Not the fault of Flask, but of how we are choosing to use it!)

import sys
reload(sys)
sys.setdefaultencoding('big5')

import info
from flask import Flask, redirect, request, url_for
from jinja2 import Environment, PackageLoader
#from OpenSSL import SSL
from werkzeug.security import generate_password_hash, check_password_hash

#from flask_sslify import SSLify


app = Flask(__name__)
#sslify = SSLify(app)
get = Environment(loader=PackageLoader(__name__, 'templates')).get_template

@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    complaint = None
    if request.method == 'POST':
        db = info.open_database()
        account_info = info.get_account_info(db, username)
        if account_info and check_password_hash(account_info[0][2], password):
            response = redirect(url_for('index'))
            response.set_cookie('username', username)
            return response
        complaint='Wrong account or password'
    return get('login.html').render(username=username, complaint=complaint)

@app.route('/logout')
def logout():
    response = redirect(url_for('login'))
    response.set_cookie('username', '')
    return response


@app.route('/forget', methods=['GET', 'POST'])
def forget():
    username = request.form.get('username', '')
    phone = request.form.get('phone', '')
    password = request.form.get('password', '')
    complaint=None
    if request.method == 'POST':
        db = info.open_database()
        account_info = info.get_account_info(db, username)
        if account_info and phone == account_info[0][3]:
            db = info.open_database()
            password = generate_password_hash(password)
            info.edit_account_info(db, username, password)
            db.commit()
            response = redirect(url_for('login'))
            return response
        complaint = 'wrong account or phone number'
    return get('forget.html').render(username=username, complaint=complaint)

@app.route('/')
def index():
    username = request.cookies.get('username')
    if not username:
        return redirect(url_for('login'))
    information = info.get_record(info.open_database(), username)
    return get('index.html').render(information=information, username=username,
        flash_messages=request.args.getlist('flash'))

@app.route('/new_user', methods=['GET', 'POST'])
def new_user():
    user_name = request.form.get('user_name', '').strip()
    password = request.form.get('password', '').strip()
    phone = request.form.get('phone', '').strip()
    complaint = None
    if request.method == 'POST':
        if user_name and password and phone:
            db = info.open_database()
            account_info = info.get_account_info(db, user_name)
            if account_info:    #null
                complaint = 'Duplicate account'
                return get('new_user.html').render(complaint=complaint, user_name=user_name, password=password, phone=phone)
            password = generate_password_hash(password)
            info.add_account(db, user_name, password, phone)
            db.commit()
            return redirect(url_for('login', flash='Account added successful'))
        complaint = ('Please fill in all three fields')
    return get('new_user.html').render(complaint=complaint, user_name=user_name, password=password, phone=phone)

@app.route('/new', methods=['GET', 'POST'])
def new():
    username = request.cookies.get('username')
    if not username:
        return redirect(url_for('login'))
    name = request.form.get('name', '').strip()
    address = request.form.get('address', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    complaint = None
    if request.method == 'POST':
        if name and address and phone and email:
            db = info.open_database()
            info.add_record(db, username, name, address, phone, email)
            db.commit()
            return redirect(url_for('index', flash='Record successful'))
        complaint = ('Please fill in all four fields')
    return get('new.html').render(complaint=complaint, name=name, address=address, phone=phone, email=email)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    username = request.cookies.get('username')
    if not username:
        return redirect(url_for('login'))
    id = request.args.get('id', '').strip()
    name = request.args.get('name', '').strip()
    address = request.args.get('address', '').strip()
    phone = request.args.get('phone', '').strip()
    email = request.args.get('email', '').strip()
    complaint = None
    return get('edit.html').render(complaint=complaint, name=name, address=address, phone=phone, email=email, id=id)

@app.route('/save',  methods=['GET', 'POST'])
def save():
    id = request.args.get('id', '').strip()
    name = request.form.get('name', '').strip()
    address = request.form.get('address', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    complaint = None
    if request.method == 'POST':
        if name and address and phone and email:
            db = info.open_database()
            info.edit_record(db, id, name, address, phone, email)
            db.commit()
            return redirect(url_for('index', flash='Edit successful'))
        complaint = ('Please fill in all three fields')
    return get('edit.html').render(complaint=complaint, name=name, address=address, phone=phone, email=email)


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    username = request.cookies.get('username')
    if not username:
        return redirect(url_for('login'))
    id = request.args.get('id', '').strip()
    db = info.open_database()
    info.del_record(db, id)
    db.commit()
    return redirect(url_for('index', flash='Delete successful'))

@app.route('/delete_user', methods=['GET', 'POST'])
def delete_user():
    username = request.cookies.get('username')
    if not username:
        return redirect(url_for('login'))
    db = info.open_database()
    info.del_user(db, username)
    db.commit()

    return redirect(url_for('logout'))


if __name__ == '__main__':

    context = ('ssl.cert', 'ssl.key')

    #app.run(host="192.168.56.102", port=8000, debug=True, threaded =True)

    app.run(host="127.0.0.1", port=8000, debug=True,  threaded =True, ssl_context='adhoc')
