import unittest
import os
import json
from app import create_app
from flask import Flask

class BudgetAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({'TESTING': True})
        self.client = self.app.test_client()

        # Create a test data file
        self.test_data_file = os.path.join(os.path.dirname(__file__), '..', 'data.json')
        with open(self.test_data_file, 'w') as f:
            json.dump([], f)

    def tearDown(self):
        # Clean up after tests
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)

    
    def test_dashboard_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome back', response.data)

    def test_add_transaction_success(self):
        response = self.client.post('/add', data={
            'description': 'Test Income',
            'amount': '5000',
            'type': 'income',
            'category': 'Other'
        }, follow_redirects=True)
        self.assertIn(b'Transaction added successfully', response.data)

    def test_add_transaction_invalid(self):
        response = self.client.post('/add', data={
            'description': '',
            'amount': '0',
            'type': 'income',
            'category': 'Other'
        }, follow_redirects=True)
        self.assertIn(b'Description is required', response.data)

    def test_add_transaction_invalid_amount(self):
        response = self.client.post('/add', data={
            'description': 'Test Expense',
            'amount': '-100',
            'type': 'expense',
            'category': 'Food'
        }, follow_redirects=True)
        self.assertIn(b'Amount must be positive', response.data)


    def test_add_transaction_invalid_type(self):
        response = self.client.post('/add', data={
            'description': 'Test Transaction',
            'amount': '1000',
            'type': 'invalid_type',
            'category': 'Other'
        }, follow_redirects=True)
        self.assertIn(b'Invalid transaction type', response.data)


    def test_add_transaction_invalid_category(self):
        response = self.client.post('/add', data={
            'description': 'Test Transaction',
            'amount': '1000',
            'type': 'expense',
            'category': ''
        }, follow_redirects=True)
        self.assertIn(b'Category is required', response.data)


    def test_add_transaction_ignores_user_date_input(self):
        response = self.client.post('/add', data={
            'description': 'Ignore Date Field',
            'amount': '150',
            'type': 'income',
            'category': 'Other',
            'date': 'not-a-real-date'  # Should be ignored
    }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Transaction added successfully!', response.data)

def test_flash_success_message(self):
    response = self.client.post('/add', data={
        'description': 'Test success',
        'amount': '100',
        'type': 'income',
        'category': 'Food'
    }, follow_redirects=True)

    self.assertIntIn(b'Transaction added successfully', response.data)


def test_flash_error_on_missing_description(self):
    response = self.client.post('/add', data={
        'description': '',
        'amount': '100',
        'type': 'income',
        'category': 'Food'
    }, follow_redirects=True)

    self.assertIn(b'Description is required', response.data)


def test_dashboard_ui_elements(self):
    response = self.client.get('/')
    html = response.data.decode()

    self.assertIn('Total Income', html)
    self.assertIn('Total Expenses', html)
    self.assertIn('Net Balance', html)
    self.assertIn('Add', html)  # Submit button
    self.assertIn('Transaction Analytics', html)


def test_dashboard_js_hooks_exist(self):
    response = self.client.get('/')
    html = response.data.decode()

    self.assertIn('id="transactions-data"', html)
    self.assertIn('id="categoryChart"', html)
    self.assertIn('id="monthlyTrendChart"', html)
    self.assertIn('id="settingsToggle"', html)

def test_transaction_displayed_on_dashboard(self):
    # Add a transaction first
    self.client.post('/add', data={
        'description': 'Display test',
        'amount': '123.45',
        'type': 'income',
        'category': 'Other'
    }, follow_redirects=True)

    # Then check it's on the dashboard
    response = self.client.get('/')
    html = response.data.decode()
    self.assertIn('Display test', html)
    self.assertIn('R 123.45', html)
