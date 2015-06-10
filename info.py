#!/usr/bin/env python3
# Foundations of Python Network Programming, Third Edition
# https://github.com/brandon-rhodes/fopnp/blob/m/py3/chapter11/bank.py
# A small library of database routines to power a payments application.

import os, pprint, sqlite3
from collections import namedtuple

def open_database(path='info.db'):
    new = not os.path.exists(path)
    db = sqlite3.connect(path)
    if new:
        c = db.cursor()
        c.execute('CREATE TABLE information (id INTEGER PRIMARY KEY,'
                  'user_name TEXT, name TEXT, address TEXT, phone TEXT, email TEXT)')
        c.execute('CREATE TABLE account (id INTEGER PRIMARY KEY,'
                  'user_name TEXT, password TEXT, phone TEXT)')
        db.commit()
    return db

def add_record(db, user_name, name, address, phone, email):
    db.cursor().execute('INSERT INTO information (user_name, name, address, phone, email)'
                        ' VALUES (?, ?, ?, ?, ?)', (user_name, name, address, phone, email))

def add_account(db, user_name, password, phone):
    db.cursor().execute('INSERT INTO account (user_name, password, phone)'
                        ' VALUES (?, ?, ?)', (user_name, password, phone))

def get_account_info(db, user_name):
    c = db.cursor()
    c.execute('SELECT * FROM account WHERE user_name = ?'
              , (user_name,))
    Row = namedtuple('Row', [tup[0] for tup in c.description])
    return [Row(*row) for row in c.fetchall()]

def edit_account_info(db, user_name, password):
    db.cursor().execute('UPDATE account '
                        'SET password = ?'
                        ' WHERE user_name = ?', (password, user_name))

def get_record(db, user_name):
    c = db.cursor()
    c.execute('SELECT * FROM information WHERE user_name = ?'
              ' ORDER BY id', (user_name,))
    Row = namedtuple('Row', [tup[0] for tup in c.description])
    return [Row(*row) for row in c.fetchall()]

def del_record(db, id_num):
    db.cursor().execute('DELETE FROM information '
                        ' WHERE id = ?', (id_num,))

def del_user(db, user_name):
    db.cursor().execute('DELETE FROM information '
                        ' WHERE user_name = ?', (user_name,))
    db.cursor().execute('DELETE FROM account '
                        ' WHERE user_name = ?', (user_name,))

def edit_record(db, id_num, name, address, phone, email):
    db.cursor().execute('UPDATE information '
                        'SET name = ?, address = ?, phone = ?, email = ?'
                        ' WHERE id = ?', (name, address, phone, email, id_num))
if __name__ == '__main__':
    db = open_database()
    pprint.pprint(get_payments_of(db, 'brandon'))
