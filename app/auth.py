from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db
from datetime import datetime

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Please fill in all fields', 'danger')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(email=email).first()

        if not user:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))

        if not user.check_password(password):  # Use the model method
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user)
        user.last_login = datetime.utcnow()  # Track login time
        db.session.commit()
        
        flash(f'Welcome, {user.username}!', 'success')
        return redirect(url_for('main.index'))

    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.landing'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.landing'))  # Redirect if already logged in

    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Simple validation
        if not email or not username or not password or not confirm_password:
            flash('Please fill in all fields.', 'warning')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'warning')
            return redirect(url_for('auth.register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.', 'warning')
            return redirect(url_for('auth.register'))

        # Create new user
        new_user = User(
            email=email,
            username=username
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')
