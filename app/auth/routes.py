# app/auth/routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from . import bp
from .forms import LoginForm, RegistrationForm
from ..models import User
from ..extensions import db

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) # Redirect to upload page if logged in
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        flash(f'Welcome back, {user.username}!', 'success')
        next_page = request.args.get('next')
        # Redirect to next page or main index (upload)
        return redirect(next_page or url_for('main.index'))
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)