import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app, db
from app.models.user import User
from app.models.transaction import Transaction

class TransactionTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False
        })
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create a test user
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password')
        db.session.add(self.user)
        db.session.commit()

        # Log in the test user
        self.client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_transaction(self):
        response = self.client.post('/add', data={
            'description': 'Test Income',
            'amount': 100,
            'type': 'income',
            'category': 'Salary'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Income', response.data)

    def test_edit_transaction(self):
        # First, add a transaction
        transaction = Transaction(description='Test Expense', amount=50, type='expense', category='Food', user_id=self.user.id)
        db.session.add(transaction)
        db.session.commit()

        # Now, edit the transaction
        response = self.client.post(f'/edit/{transaction.id}', data={
            'description': 'Updated Expense',
            'amount': 75,
            'type': 'expense',
            'category': 'Groceries'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Updated Expense', response.data)
        self.assertNotIn(b'Test Expense', response.data)

    def test_delete_transaction(self):
        # First, add a transaction
        transaction = Transaction(description='Test Expense', amount=50, type='expense', category='Food', user_id=self.user.id)
        db.session.add(transaction)
        db.session.commit()

        # Now, delete the transaction
        response = self.client.post(f'/delete/{transaction.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Test Expense', response.data)

if __name__ == '__main__':
    unittest.main()
