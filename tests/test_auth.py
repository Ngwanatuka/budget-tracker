import unittest
from app import create_app, db
from app.models.user import User

class AuthTestCase(unittest.TestCase):

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

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register_user(self):
        response = self.client.post('/auth/register', data={
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'password',
            'confirm_password': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful! Please log in.', response.data)

    def test_register_existing_user(self):
        # Register a user first
        self.client.post('/auth/register', data={
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'password',
            'confirm_password': 'password'
        }, follow_redirects=True)
        # Try to register again with the same email
        response = self.client.post('/auth/register', data={
            'email': 'test@example.com',
            'username': 'newuser',
            'password': 'newpassword',
            'confirm_password': 'newpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email already registered.', response.data)

    def test_login_user(self):
        # Register a user first
        self.client.post('/auth/register', data={
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'password',
            'confirm_password': 'password'
        }, follow_redirects=True)
        # Now, log in
        response = self.client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome, testuser!', response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post('/auth/login', data={
            'email': 'wrong@example.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email or password', response.data)

    def test_logout_user(self):
        # Register and log in a user
        self.client.post('/auth/register', data={'email': 'test@example.com', 'username': 'testuser', 'password': 'password', 'confirm_password': 'password'}, follow_redirects=True)
        self.client.post('/auth/login', data={'email': 'test@example.com', 'password': 'password'}, follow_redirects=True)
        # Logout
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged out.', response.data)

if __name__ == '__main__':
    unittest.main()
