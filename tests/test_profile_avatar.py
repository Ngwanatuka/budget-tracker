import os
import unittest
from flask import url_for
from app import create_app, db
from app.models.user import User

class ProfileAvatarTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False, # Disable CSRF for testing
            'UPLOAD_FOLDER': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_avatars'),
            'ALLOWED_EXTENSIONS': {'png', 'jpg', 'jpeg', 'gif'}
        })
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            # Ensure upload folder exists for testing
            os.makedirs(self.app.config['UPLOAD_FOLDER'], exist_ok=True)

            # Create a test user
            user = User(username='testuser', email='test@example.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            # Clean up test avatar folder
            if os.path.exists(self.app.config['UPLOAD_FOLDER']):
                for filename in os.listdir(self.app.config['UPLOAD_FOLDER']):
                    os.remove(os.path.join(self.app.config['UPLOAD_FOLDER'], filename))
                os.rmdir(self.app.config['UPLOAD_FOLDER'])

    def login(self, email, password):
        return self.client.post('/auth/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def test_profile_update(self):
        with self.app.app_context():
            self.login('test@example.com', 'password')

            # Test updating username and email
            response = self.client.post('/profile', data=dict(
                username='newusername',
                email='newemail@example.com'
            ), follow_redirects=True)
            self.assertIn(b'Profile updated successfully!', response.data)

            updated_user = db.session.get(User, self.user_id)
            self.assertEqual(updated_user.username, 'newusername')
            self.assertEqual(updated_user.email, 'newemail@example.com')

    def test_avatar_upload_valid(self):
        with self.app.app_context():
            self.login('test@example.com', 'password')

            # Create a dummy image file
            dummy_image_path = os.path.join(self.app.config['UPLOAD_FOLDER'], 'test_avatar.png')
            with open(dummy_image_path, 'wb') as f:
                f.write(b'dummy_png_content')

            with open(dummy_image_path, 'rb') as img:
                response = self.client.post('/profile', data=dict(
                    username='testuser',
                    email='test@example.com',
                    avatar=(img, 'test_avatar.png')
                ), follow_redirects=True)
            self.assertIn(b'Profile updated successfully!', response.data)

            updated_user = db.session.get(User, self.user_id)
            self.assertIsNotNone(updated_user.avatar_url)
            self.assertIn('/static/avatars/1_test_avatar.png', updated_user.avatar_url)

    def test_avatar_upload_invalid_type(self):
        with self.app.app_context():
            self.login('test@example.com', 'password')

            # Create a dummy text file (invalid type)
            dummy_file_path = os.path.join(self.app.config['UPLOAD_FOLDER'], 'test_invalid.txt')
            with open(dummy_file_path, 'w') as f:
                f.write('dummy text content')

            with open(dummy_file_path, 'rb') as invalid_file:
                response = self.client.post('/profile', data=dict(
                    username='testuser',
                    email='test@example.com',
                    avatar=(invalid_file, 'test_invalid.txt')
                ), follow_redirects=True)
            self.assertIn(b'Invalid file type for avatar. Allowed types are png, jpg, jpeg, gif.', response.data)

            updated_user = db.session.get(User, self.user_id)
            self.assertIsNone(updated_user.avatar_url) # Avatar URL should not be updated

if __name__ == '__main__':
    unittest.main()
