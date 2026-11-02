import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-before-deploying')
db_url = os.environ.get('DATABASE_URL', 'sqlite:///bulochka.db')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='worker')
    active = db.Column(db.Boolean, default=True)

class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    address = db.Column(db.String(255), default='')
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Audit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(100), nullable=False)
    detail = db.Column(db.String(500), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        # Change this temporary password immediately after first login.
        db.session.add(User(username='admin', password_hash=generate_password_hash(os.environ.get('INITIAL_ADMIN_PASSWORD', 'ChangeMe123!')), role='admin'))
        db.session.commit()

def current_user():
    if 'uid' not in session:
        return None
    return db.session.get(User, session['uid'])

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user():
            return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        u = current_user()
        if not u or u.role != 'admin':
            flash('Bu bo‘lim faqat admin uchun.')
            return redirect(url_for('dashboard'))
        return fn(*args, **kwargs)
    return wrapper

def audit(action, detail=''):
    u = current_user()
    db.session.add(Audit(user_id=u.id if u else None, action=action, detail=detail))
    db.session.commit()

@app.route('/')
def index():
    return redirect(url_for('dashboard') if current_user() else url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = User.query.filter_by(username=request.form.get('username','').strip(), active=True).first()
        if u and check_password_hash(u.password_hash, request.form.get('password','')):
            session['uid'] = u.id
            audit('login', 'Tizimga kirdi')
            return redirect(url_for('dashboard'))
        flash('Login yoki parol noto‘g‘ri.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    audit('logout', 'Tizimdan chiqdi')
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    u = current_user()
    shops = Shop.query.order_by(Shop.name).all()
    users_count = User.query.filter_by(active=True).count() if u.role == 'admin' else None
    logs = Audit.query.order_by(Audit.created_at.desc()).limit(8).all() if u.role == 'admin' else []
    return render_template('dashboard.html', user=u, shops=shops, users_count=users_count, logs=logs)

@app.route('/shops/add', methods=['POST'])
@login_required
@admin_required
def add_shop():
    name = request.form.get('name','').strip()
    address = request.form.get('address','').strip()
    try:
        lat = float(request.form.get('lat'))
        lng = float(request.form.get('lng'))
        if not (-90 <= lat <= 90 and -180 <= lng <= 180): raise ValueError()
    except (TypeError, ValueError):
        flash('Do‘konni xaritaga qo‘yish uchun GPS koordinatasi kerak.')
        return redirect(url_for('dashboard'))
    if not name:
        flash('Do‘kon nomini kiriting.')
        return redirect(url_for('dashboard'))
    s = Shop(name=name, address=address, lat=lat, lng=lng)
    db.session.add(s); db.session.commit()
    audit('shop_added', f'{name} | {lat}, {lng}')
    flash('Do‘kon xaritaga qo‘shildi.')
    return redirect(url_for('dashboard'))

@app.route('/api/shops')
@login_required
def api_shops():
    return jsonify([{'id':s.id,'name':s.name,'address':s.address,'lat':s.lat,'lng':s.lng} for s in Shop.query.all()])

@app.route('/workers/add', methods=['POST'])
@login_required
@admin_required
def add_worker():
    username = request.form.get('username','').strip()
    password = request.form.get('password','')
    if len(username) < 3 or len(password) < 10:
        flash('Login kamida 3 belgi, parol kamida 10 belgidan iborat bo‘lsin.')
    elif User.query.filter_by(username=username).first():
        flash('Bu login band.')
    else:
        db.session.add(User(username=username, password_hash=generate_password_hash(password), role='worker'))
        db.session.commit(); audit('worker_added', username); flash('Ishchi qo‘shildi.')
    return redirect(url_for('dashboard'))

@app.route('/health')
def health():
    return {'status':'ok','app':'BULOCHKA CONTROL'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
