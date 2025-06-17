import json
import os
from flask import Blueprint, render_template, request, redirect, url_for

bp = Blueprint('main', __name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data.json')

def load_transactions():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_transactions(transactions):
    with open(DATA_FILE, 'w') as f:
        json.dump(transactions, f, indent=2)

@bp.route('/')
def dashboard():
    transactions = load_transactions()
    income = sum(t['amount'] for t in transactions if t['type'] == 'income')
    expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    balance = income - expenses

    return render_template('dashboard.html',
                           transactions=transactions,
                           income=income,
                           expenses=expenses,
                           balance=balance)

@bp.route('/add', methods=['POST'])
def add_transaction():
    transactions = load_transactions()

    description = request.form['description']
    amount = float(request.form['amount'])
    t_type = request.form['type']
    category = request.form['category']

    new_transaction = {
        'description': description,
        'amount': amount,
        'type': t_type,
        'category': category
    }

    transactions.append(new_transaction)
    save_transactions(transactions)

    return redirect(url_for('main.dashboard'))
