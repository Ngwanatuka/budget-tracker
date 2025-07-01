import unittest
from app import create_app, db
from app.models.user import User
from app.models.transaction import Transaction
from flask import get_flashed_messages

class BudgetAppRouteTestCase(unittest.TestCase):
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

    def test_dashboard_loads_authenticated(self):
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome back, testuser', response.data)

    def test_add_transaction_success(self):
        response = self.client.post('/add', data={
            'description': 'Test Income',
            'amount': '5000',
            'type': 'income',
            'category': 'Other'
        }, follow_redirects=True)
        self.assertIn(b'Transaction added successfully!', response.data)

    def test_add_transaction_missing_description(self):
        response = self.client.post('/add', data={
            'description': '',
            'amount': '100',
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

    def test_add_transaction_missing_category(self):
        response = self.client.post('/add', data={
            'description': 'Test Transaction',
            'amount': '1000',
            'type': 'expense',
            'category': ''
        }, follow_redirects=True)
        self.assertIn(b'Category is required', response.data)

    def test_transaction_displayed_on_dashboard(self):
        # Add a transaction first
        self.client.post('/add', data={
            'description': 'Display test',
            'amount': '123.45',
            'type': 'income',
            'category': 'Other'
        }, follow_redirects=True)

        # Then check it's on the dashboard
        response = self.client.get('/dashboard')
        self.assertIn(b'Display test', response.data)
        self.assertIn(b'123.45', response.data)

    def test_reset_data(self):
        # Add a transaction
        self.client.post('/add', data={'description': 'Test', 'amount': '100', 'type': 'income', 'category': 'Test'}, follow_redirects=True)
        
        # Reset data
        response = self.client.post('/reset', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Check that the transaction is gone
        self.assertNotIn(b'Test', response.data)
        
        # Check for the flash message
        with self.app.test_request_context():
            # Manually trigger session handling to get flashed messages
            with self.client.session_transaction() as session:
                flashed_messages = session.get('_flashes', [])
        
        # This is a workaround. A better way is to check the response data directly
        # as the flash message should be rendered in the redirected page.
        self.assertIn(b'All data has been reset.', response.data)

if __name__ == '__main__':
    unittest.main()


