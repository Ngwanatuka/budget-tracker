import unittest
import sys
import os
from datetime import datetime, timedelta, timezone
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

    def test_edit_other_users_transaction(self):
        # Create another user
        other_user = User(username='otheruser', email='other@example.com')
        other_user.set_password('password')
        db.session.add(other_user)
        db.session.commit()

        # Add a transaction for the other user
        transaction = Transaction(description='Other User Transaction', amount=100, type='income', category='Salary', user_id=other_user.id)
        db.session.add(transaction)
        db.session.commit()

        # Try to edit the other user's transaction
        response = self.client.post(f'/edit/{transaction.id}', data={
            'description': 'Updated Transaction',
            'amount': 150,
            'type': 'income',
            'category': 'Bonus'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You do not have permission to edit this transaction.', response.data)

    def test_delete_other_users_transaction(self):
        # Create another user
        other_user = User(username='otheruser', email='other@example.com')
        other_user.set_password('password')
        db.session.add(other_user)
        db.session.commit()

        # Add a transaction for the other user
        transaction = Transaction(description='Other User Transaction', amount=100, type='income', category='Salary', user_id=other_user.id)
        db.session.add(transaction)
        db.session.commit()

        # Try to delete the other user's transaction
        response = self.client.post(f'/delete/{transaction.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You do not have permission to delete this transaction.', response.data)

    def test_transaction_pagination(self):
        # Add 20 transactions with distinct dates to ensure consistent ordering
        for i in range(20, 0, -1):  # Add from 20 down to 1 to ensure descending order by date
            transaction = Transaction(description=f'Test Transaction {i}', amount=i * 10, type='income', category='Category', user_id=self.user.id, date=datetime.now(timezone.utc) - timedelta(seconds=i))
            db.session.add(transaction)
        db.session.commit()

        # Test first page (per_page is 5)
        response = self.client.get('/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Transaction 1', response.data)
        self.assertIn(b'Test Transaction 5', response.data)
        self.assertNotIn(b'Test Transaction 6', response.data)

        # Test second page
        response = self.client.get('/dashboard?page=2', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Transaction 6', response.data)
        self.assertIn(b'Test Transaction 10', response.data)
        self.assertNotIn(b'Test Transaction 5', response.data)
        self.assertNotIn(b'Test Transaction 11', response.data)

        # Test third page
        response = self.client.get('/dashboard?page=3', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Transaction 11', response.data)
        self.assertIn(b'Test Transaction 15', response.data)
        self.assertNotIn(b'Test Transaction 10', response.data)
        self.assertNotIn(b'Test Transaction 16', response.data)

        # Test fourth page
        response = self.client.get('/dashboard?page=4', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Transaction 16', response.data)
        self.assertIn(b'Test Transaction 20', response.data)
        self.assertNotIn(b'Test Transaction 15', response.data)

        # Test an invalid page number
        response = self.client.get('/dashboard?page=999', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No transactions yet', response.data)

    def test_total_income_expense_net_income_with_pagination(self):
        # Add a mix of income and expense transactions
        transactions_to_add = [
            {'description': 'Salary', 'amount': 1000, 'type': 'income'},
            {'description': 'Rent', 'amount': 500, 'type': 'expense'},
            {'description': 'Bonus', 'amount': 200, 'type': 'income'},
            {'description': 'Groceries', 'amount': 150, 'type': 'expense'},
            {'description': 'Freelance', 'amount': 300, 'type': 'income'},
            {'description': 'Utilities', 'amount': 100, 'type': 'expense'},
            {'description': 'Gift', 'amount': 50, 'type': 'income'},
            {'description': 'Dinner', 'amount': 75, 'type': 'expense'},
            {'description': 'Investment', 'amount': 1000, 'type': 'income'},
            {'description': 'Shopping', 'amount': 250, 'type': 'expense'},
            {'description': 'Refund', 'amount': 80, 'type': 'income'},
            {'description': 'Transport', 'amount': 40, 'type': 'expense'},
        ]

        expected_total_income = 0
        expected_total_expenses = 0
        for i, data in enumerate(transactions_to_add):
            transaction = Transaction(
                description=data['description'],
                amount=data['amount'],
                type=data['type'],
                category='Test Category',
                user_id=self.user.id,
                date=datetime.now(timezone.utc) - timedelta(seconds=i) # Ensure distinct dates
            )
            db.session.add(transaction)
            if data['type'] == 'income':
                expected_total_income += data['amount']
            else:
                expected_total_expenses += data['amount']
        db.session.commit()

        expected_net_income = expected_total_income - expected_total_expenses

        # Access the dashboard (first page)
        response = self.client.get('/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Verify the displayed totals match the expected totals
        self.assertIn(f'R {expected_total_income:.1f}'.encode(), response.data)
        self.assertIn(f'R {expected_total_expenses:.1f}'.encode(), response.data)
        self.assertIn(f'R {expected_net_income:.1f}'.encode(), response.data)

        # Access a different page (e.g., second page) and verify totals are still correct
        response = self.client.get('/dashboard?page=2', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        self.assertIn(f'R {expected_total_income:.1f}'.encode(), response.data)
        self.assertIn(f'R {expected_total_expenses:.1f}'.encode(), response.data)
        self.assertIn(f'R {expected_net_income:.1f}'.encode(), response.data)


if __name__ == '__main__':
    unittest.main()