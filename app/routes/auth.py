import json
import os
import re
import hmac
import hashlib
import time
import secrets as py_secrets
import requests
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import User
from app.config import Config
from app.utils import filter_sensitive
from app.i18n import t

auth_bp = Blueprint('auth', __name__)


# ---------- Rate Limiting ----------

def rate_limit(key, max_attempts=5, window=300):
    """Simple session-based rate limiter. Returns True if rate limited."""
    now = time.time()
    attempts = session.get(key, [])
    attempts = [t for t in attempts if now - t < window]
    if len(attempts) >= max_attempts:
        session[key] = attempts
        return True
    attempts.append(now)
    session[key] = attempts
    return False


# ---------- OAuth State Signing ----------

def sign_state(state_data):
    """Sign OAuth state to prevent tampering."""
    sig = hmac.new(Config.SECRET_KEY.encode(), state_data.encode(), hashlib.sha256).hexdigest()[:16]
    return f'{state_data}.{sig}'


def verify_state(state):
    """Verify OAuth state signature. Returns the state data or None."""
    if not state or '.' not in state:
        return None
    data, sig = state.rsplit('.', 1)
    expected = hmac.new(Config.SECRET_KEY.encode(), data.encode(), hashlib.sha256).hexdigest()[:16]
    if hmac.compare_digest(sig, expected):
        return data
    return None


# ---------- Routes ----------

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))
    if request.method == 'POST':
        if rate_limit('login_attempts', max_attempts=5, window=300):
            flash(t('error_rate_limit'), 'error')
            return redirect(url_for('auth.login'))
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and user.check_password(password):
            if not user.is_active:
                flash(t('error_account_disabled'), 'error')
                return redirect(url_for('auth.login'))
            login_user(user, remember=remember)
            session.pop('login_attempts', None)
            next_page = request.args.get('next')
            if next_page and (not next_page.startswith('/') or next_page.startswith('//')):
                next_page = None
            return redirect(next_page or url_for('blog.index'))
        flash(t('error_login_failed'), 'error')
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))
    if request.method == 'POST':
        if rate_limit('register_attempts', max_attempts=3, window=600):
            flash(t('error_rate_limit'), 'error')
            return redirect(url_for('auth.register'))
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')

        if not all([username, email, password]):
            flash(t('error_fill_required'), 'error')
            return redirect(url_for('auth.register'))
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
            flash(t('email') + ' ' + t('error_fill_required').lower(), 'error')
            return redirect(url_for('auth.register'))
        if len(username) < 3 or len(username) > 20:
            flash(t('error_username_length'), 'error')
            return redirect(url_for('auth.register'))
        if password != confirm:
            flash(t('error_password_mismatch'), 'error')
            return redirect(url_for('auth.register'))
        if len(password) < 6:
            flash(t('error_password_short'), 'error')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(username=username).first():
            flash(t('error_username_exists'), 'error')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=email).first():
            flash(t('error_email_exists'), 'error')
            return redirect(url_for('auth.register'))

        if filter_sensitive(username) != username:
            flash(t('error_sensitive_username'), 'error')
            return redirect(url_for('auth.register'))

        user = User(username=username, email=email, role='user')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(t('toast_register_success'), 'success')
        return redirect(url_for('blog.index'))
    return render_template('auth/register.html')


@auth_bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    flash(t('toast_logout'), 'success')
    return redirect(url_for('blog.index'))


@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    # Step 3: After GitHub OAuth verified — set new password
    if request.method == 'POST' and session.get('reset_verified_user_id'):
        new_password = request.form.get('new_password', '')
        confirm = request.form.get('confirm', '')

        if not all([new_password, confirm]):
            flash(t('error_fill_required'), 'error')
            return render_template('auth/reset_password.html', step='set_password')

        if new_password != confirm:
            flash(t('error_password_mismatch'), 'error')
            return render_template('auth/reset_password.html', step='set_password')
        if len(new_password) < 6:
            flash(t('error_password_short'), 'error')
            return render_template('auth/reset_password.html', step='set_password')

        user_id = session.pop('reset_verified_user_id')
        user = User.query.get(user_id)
        if user:
            user.set_password(new_password)
            db.session.commit()
        session.pop('reset_verified_user_id', None)
        session.pop('reset_email', None)
        flash(t('toast_password_reset'), 'success')
        return redirect(url_for('auth.login'))

    # Step 1: Enter email
    if request.method == 'POST' and not session.get('reset_verified_user_id'):
        if rate_limit('reset_attempts', max_attempts=3, window=600):
            flash(t('error_rate_limit'), 'error')
            return redirect(url_for('auth.reset_password'))
        email = request.form.get('email', '').strip()
        if not email:
            flash(t('error_fill_required'), 'error')
            return redirect(url_for('auth.reset_password'))
        user = User.query.filter_by(email=email).first()
        if not user:
            flash(t('error_email_not_found'), 'error')
            return redirect(url_for('auth.reset_password'))
        # Store email in session, redirect to GitHub OAuth
        session['reset_email'] = email
        session['reset_via_github'] = True
        return redirect(url_for('auth.github_login'))

    return render_template('auth/reset_password.html')


# ---------- GitHub OAuth ----------

@auth_bp.route('/github')
def github_login():
    if not Config.GITHUB_CLIENT_ID:
        flash(t('error_github_not_configured'), 'error')
        return redirect(url_for('auth.login'))

    # Build redirect URI
    space_host = os.environ.get('SPACE_HOST', '')
    if Config.SITE_URL:
        redirect_uri = Config.SITE_URL.rstrip('/') + url_for('auth.github_callback')
    elif space_host:
        redirect_uri = f'https://{space_host}' + url_for('auth.github_callback')
    else:
        redirect_uri = request.host_url.rstrip('/') + url_for('auth.github_callback')

    # If this is a password reset flow, add state parameter with HMAC signature
    if session.get('reset_via_github'):
        state = sign_state('reset_password')
    else:
        state = sign_state('login')

    url = (
        f'https://github.com/login/oauth/authorize?client_id={Config.GITHUB_CLIENT_ID}'
        f'&redirect_uri={redirect_uri}&scope=user:email&state={state}'
    )
    return redirect(url)


@auth_bp.route('/github/callback')
def github_callback():
    code = request.args.get('code')
    raw_state = request.args.get('state', '')
    state = verify_state(raw_state)
    if not code or not state:
        flash(t('error_github_failed'), 'error')
        return redirect(url_for('auth.login'))

    resp = requests.post('https://github.com/login/oauth/access_token', json={
        'client_id': Config.GITHUB_CLIENT_ID,
        'client_secret': Config.GITHUB_CLIENT_SECRET,
        'code': code,
    }, headers={'Accept': 'application/json'})
    data = resp.json()
    token = data.get('access_token')
    if not token:
        flash(t('error_github_failed'), 'error')
        return redirect(url_for('auth.login'))

    user_resp = requests.get('https://api.github.com/user', headers={'Authorization': f'token {token}'})
    gh_user = user_resp.json()
    github_id = str(gh_user.get('id', ''))

    email_resp = requests.get('https://api.github.com/user/emails', headers={'Authorization': f'token {token}'})
    emails = email_resp.json()
    primary_email = ''
    if isinstance(emails, list):
        for e in emails:
            if e.get('primary'):
                primary_email = e.get('email', '')
                break

    # --- Password reset flow ---
    if state == 'reset_password' and session.get('reset_via_github'):
        session.pop('reset_via_github', None)
        reset_email = session.get('reset_email', '')

        if not reset_email:
            flash(t('error_code_expired'), 'error')
            return redirect(url_for('auth.reset_password'))

        # Verify GitHub primary email matches the registered email
        if primary_email.lower() != reset_email.lower():
            # Also check all GitHub emails
            gh_emails = []
            if isinstance(emails, list):
                gh_emails = [e.get('email', '').lower() for e in emails]
            if reset_email.lower() not in gh_emails:
                session.pop('reset_email', None)
                flash(t('error_github_email_mismatch'), 'error')
                return redirect(url_for('auth.reset_password'))

        user = User.query.filter_by(email=reset_email).first()
        if not user:
            session.pop('reset_email', None)
            flash(t('error_email_not_found'), 'error')
            return redirect(url_for('auth.reset_password'))

        # Verified — allow password reset
        session['reset_verified_user_id'] = user.id
        return render_template('auth/reset_password.html', step='set_password')

    # --- Normal login/register flow ---
    user = User.query.filter_by(github_id=github_id).first()
    if not user and primary_email:
        user = User.query.filter_by(email=primary_email).first()

    if user:
        if not user.github_id:
            user.github_id = github_id
            db.session.commit()
        login_user(user)
        flash(t('toast_login_success'), 'success')
    else:
        username = gh_user.get('login', f'gh_{github_id}')
        base = username
        n = 1
        while User.query.filter_by(username=username).first():
            username = f'{base}_{n}'
            n += 1
        user = User(
            username=username,
            email=primary_email or f'{github_id}@github.com',
            github_id=github_id,
            avatar=gh_user.get('avatar_url', ''),
            bio=gh_user.get('bio', '') or '',
            role='user',
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(t('toast_register_success'), 'success')

    return redirect(url_for('blog.index'))
