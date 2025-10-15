from flask import Flask, render_template, request, redirect, url_for, session
import random
import string

app = Flask(__name__)
app.secret_key = 'secret-key'


def user_exists(username):
    try:
        with open('UserPass.txt', 'r', encoding='utf-8') as f:
            for line in f:
                stored_username, _ = line.strip().split(':')
                if stored_username == username:
                    return True
    except FileNotFoundError:
        pass
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

        with open('UserPass.txt', 'a', encoding='utf-8') as f:
            f.write(f"{username}:{password}\n")

        session['username'] = username
        return redirect(url_for('generator'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            with open('UserPass.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    stored_username, stored_password = line.strip().split(':')
                    if stored_username == username and stored_password == password:
                        session['username'] = username
                        return redirect(url_for('generator'))
        except FileNotFoundError:
            pass

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

    passwords = []

    if request.method == 'POST':
        length = int(request.form.get('length', 12))

        use_uppercase = 'uppercase' in request.form
        use_lowercase = 'lowercase' in request.form
        use_digits = 'digits' in request.form
        use_special = 'special' in request.form

        for _ in range(5):
            password = generate_password(length, use_uppercase, use_lowercase, use_digits, use_special)
            passwords.append(password)

    return render_template('generator.html', passwords=passwords, username=session['username'])


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
