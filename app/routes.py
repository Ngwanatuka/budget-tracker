from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Transaction
from . import db
from datetime import datetime
import json

bp = Blueprint('main', __name__)

@bp.route('/dashboard')
def dashboard():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    
    income = sum(t.amount for t in transactions if t.type == 'income')
    expenses = sum(t.amount for t in transactions if t.type == 'expense')
    balance = income - expenses

    transactions_data = json.dumps([
        {
            'id': t.id,
            'description': t.description,
            'amount': t.amount,
            'type': t.type,
            'category': t.category,
            'date': t.date.isoformat()
        }
        for t in transactions
    ])

    return render_template('dashboard.html',
                           transactions=transactions,
                           income=income,
                           expenses=expenses,
                           balance=balance,
                           transactions_data=transactions_data)


@bp.route('/')
def landing():
    return render_template('landing.html', datetime=datetime)


@bp.route('/reset', methods=['POST'])
def reset_data():
    try:
        Transaction.query.delete()
        db.session.commit()
        flash('All data has been reset.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error resetting data.', 'error')

    return redirect(url_for('main.dashboard'))



@bp.route('/add', methods=['POST'])
def add_transaction():
    try:
        description = request.form['description'].strip()
        if not description:
            flash('Description is required', 'error')
            return redirect(url_for('main.dashboard'))

        amount = float(request.form['amount'])
        if amount <= 0:
            flash('Amount must be positive', 'error')
            return redirect(url_for('main.dashboard'))

        t_type = request.form['type'].strip().lower()
        if t_type not in ['income', 'expense']:
            flash('Invalid transaction type', 'error')
            return redirect(url_for('main.dashboard'))

        category = request.form['category'].strip()
        if not category:
            flash('Category is required', 'error')
            return redirect(url_for('main.dashboard'))

        new_transaction = Transaction(
            description=description,
            amount=amount,
            type=t_type,
            category=category,
            date=datetime.utcnow()
        )

        db.session.add(new_transaction)
        db.session.commit()
        flash('Transaction added successfully!', 'success')

    except ValueError:
        flash('Invalid amount format', 'error')

    return redirect(url_for('main.dashboard'))