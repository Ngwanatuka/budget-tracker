import json
import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash

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

def get_next_id(transactions):
    return max(t['id'] for t in transactions) + 1 if transactions else 1

@bp.route('/')
def dashboard():
    transactions = load_transactions()
    
    # Calculate totals
    income = sum(t['amount'] for t in transactions if t['type'] == 'income')
    expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    balance = income - expenses
    
    # Prepare data for JavaScript
    transactions_data = json.dumps([
        {
            'id': t['id'],
            'description': t['description'],
            'amount': t['amount'],
            'type': t['type'],
            'category': t['category'],
            'date': t.get('date', '')  # Safely handle missing date
        }
        for t in transactions
    ])
    
    return render_template('dashboard.html',
                         transactions=transactions,
                         income=income,
                         expenses=expenses,
                         balance=balance,
                         transactions_data=transactions_data)

@bp.route('/add', methods=['POST'])
def add_transaction():
    transactions = load_transactions()
    
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
        
        new_transaction = {
            'id': get_next_id(transactions),
            'description': description,
            'amount': amount,
            'type': t_type,
            'category': category,
            'date': datetime.now().isoformat()
        }

        transactions.append(new_transaction)
        save_transactions(transactions)
        flash('Transaction added successfully!', 'success')
        
    except ValueError:
        flash('Invalid amount format', 'error')
    except KeyError as e:
        flash(f'Missing required field: {e}', 'error')

    return redirect(url_for('main.dashboard'))