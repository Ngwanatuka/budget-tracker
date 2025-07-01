from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.transaction import Transaction
from . import db
from datetime import datetime
import pytz
import json
from sqlalchemy.exc import SQLAlchemyError

bp = Blueprint('main', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of transactions per page
    transactions_pagination = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    transactions = transactions_pagination.items
    
    income = sum(t.amount for t in transactions if t.type == 'income')
    expenses = sum(t.amount for t in transactions if t.type == 'expense')
    balance = income - expenses

    # convert last login to Johannesburg timezone
    sa_timezone = pytz.timezone('Africa/Johannesburg')
    local_login_time = current_user.last_login.astimezone(sa_timezone)

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
                           transactions_data=transactions_data,
                           user=current_user,
                           local_login_time=local_login_time,
                           transactions_pagination=transactions_pagination)


@bp.route('/')
def index():
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('landing.html', datetime=datetime)


@bp.route('/reset', methods=['POST'])
def reset_data():
    try:
        Transaction.query.delete()
        db.session.commit()
        flash('All data has been reset.', 'success')
    except SQLAlchemyError as e:
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
            date=datetime.utcnow(),
            user=current_user
        )

        db.session.add(new_transaction)
        db.session.commit()
        flash('Transaction added successfully!', 'success')

    except ValueError:
        flash('Invalid amount format', 'error')

    return redirect(url_for('main.dashboard'))


@bp.route('/edit/<int:transaction_id>', methods=['POST'])
@login_required
def edit_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.user_id != current_user.id:
        flash('You do not have permission to edit this transaction.', 'danger')
        return redirect(url_for('main.dashboard'))

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

        transaction.description = description
        transaction.amount = amount
        transaction.type = t_type
        transaction.category = category
        db.session.commit()
        flash('Transaction updated successfully!', 'success')

    except ValueError:
        flash('Invalid amount format', 'error')

    return redirect(url_for('main.dashboard'))


@bp.route('/delete/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.user_id != current_user.id:
        flash('You do not have permission to delete this transaction.', 'danger')
        return redirect(url_for('main.dashboard'))

    db.session.delete(transaction)
    db.session.commit()
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('main.dashboard'))
