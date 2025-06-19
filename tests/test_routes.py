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