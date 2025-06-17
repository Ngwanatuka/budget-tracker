from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
def dashboard():
    transactions = [
        {'description': 'Salary', 'amount': 10000, 'type': 'income'},
        {'description': 'Groceries', 'amount': 1200, 'type': 'expense'}
    ]

    income = sum(t['amount'] for t in transactions if t['type'] == 'income')
    expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    balance = income - expenses

    return render_template('dashboard.html',
                           transactions=transactions,
                           income=income,
                           expenses=expenses,
                           balance=balance)
