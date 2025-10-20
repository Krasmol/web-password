from flask import Flask, render_template, request, redirect, url_for, session
import random
import string
import json
import os

app = Flask(__name__)
app.secret_key = 'secret-key'

USER_DATA_FILE = 'user_data.json'


def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_user_data(data):
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def user_exists(username):
    data = load_user_data()
    return username in data


def verify_password(username, password):
    data = load_user_data()
    if username in data:
        return data[username]['password'] == password
    return False


def get_user_passwords(username):
    data = load_user_data()
    if username in data:
        return data[username].get('saved_passwords', [])
    return []


def save_user_password(username, site, login, password):
    data = load_user_data()
    if username not in data:
        return False

    if 'saved_passwords' not in data[username]:
        data[username]['saved_passwords'] = []

    data[username]['saved_passwords'].append({
        'site': site,
        'login': login,
        'password': password
    })

    save_user_data(data)
    return True


def delete_user_password(username, index):
    data = load_user_data()
    if username in data and 'saved_passwords' in data[username]:
        if 0 <= index < len(data[username]['saved_passwords']):
            data[username]['saved_passwords'].pop(index)
            save_user_data(data)
            return True
    return False


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if user_exists(username):
            return render_template('register.html', error="Пользователь с таким логином уже существует")

        if password != confirm_password:
            return render_template('register.html', error="Пароли не совпадают")

        if len(username) < 3:
            return render_template('register.html', error="Логин должен быть не менее 3 символов")

        data = load_user_data()
        data[username] = {
            'password': password,
            'saved_passwords': []
        }
        save_user_data(data)

        session['username'] = username
        return redirect(url_for('manager'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if verify_password(username, password):
            session['username'] = username
            return redirect(url_for('manager'))

        return render_template('login.html', error="Неверный логин или пароль")

    return render_template('login.html')


def generate_password(length, use_uppercase, use_lowercase, use_digits, use_special):


    chars = ''

    if use_uppercase:
        chars += string.ascii_uppercase
    if use_lowercase:
        chars += string.ascii_lowercase
    if use_digits:
        chars += string.digits
    if use_special:
        chars += "!@#$%&*"

    if not chars:
        chars = string.ascii_letters + string.digits + "!@#$%&*"

    return ''.join(random.choice(chars) for _ in range(length))


@app.route('/generator', methods=['GET', 'POST'])
def generator():
    if 'username' not in session:
        return redirect(url_for('login'))

    generated_passwords = []

    if request.method == 'POST':
        length = int(request.form.get('length', 12))

        use_uppercase = 'uppercase' in request.form
        use_lowercase = 'lowercase' in request.form
        use_digits = 'digits' in request.form
        use_special = 'special' in request.form

        for _ in range(5):
            password = generate_password(length, use_uppercase, use_lowercase, use_digits, use_special)
            generated_passwords.append(password)

    return render_template('generator.html',
                           generated_passwords=generated_passwords,
                           username=session['username'])


@app.route('/manager', methods=['GET', 'POST'])
def manager():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    saved_passwords = get_user_passwords(username)
    generated_passwords = []

    if request.method == 'POST':
        if 'generate_passwords' in request.form:
            length = int(request.form.get('length', 12))
            use_uppercase = 'uppercase' in request.form
            use_lowercase = 'lowercase' in request.form
            use_digits = 'digits' in request.form
            use_special = 'special' in request.form

            for _ in range(5):
                password = generate_password(length, use_uppercase, use_lowercase, use_digits, use_special)
                generated_passwords.append(password)

        elif 'save_password' in request.form:
            site = request.form['site']
            login = request.form['site_login']
            selected_password = request.form['selected_password']

            if site and login and selected_password:
                save_user_password(username, site, login, selected_password)
                return redirect(url_for('manager'))

        elif 'delete_password' in request.form:
            index = int(request.form['delete_password'])
            delete_user_password(username, index)
            return redirect(url_for('manager'))

    return render_template('manager.html',
                           username=username,
                           saved_passwords=saved_passwords,
                           generated_passwords=generated_passwords)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
