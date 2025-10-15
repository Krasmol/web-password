from flask import Flask, render_template, request, redirect, url_for, session
import random
import string

app = Flask(__name__)
app.secret_key = 'secret-key'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('register.html', error="Пароли не совпадают")

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


@app.route('/generator', methods=['GET', 'POST'])
def generator():
    if 'username' not in session:
        return redirect(url_for('login'))

    passwords = []

    if request.method == 'POST':
        length = int(request.form.get('length', 12))
        for _ in range(5):
            chars = string.ascii_letters + string.digits + "!@#$%"
            password = ''.join(random.choice(chars) for _ in range(length))
            passwords.append(password)

    return render_template('generator.html', passwords=passwords, username=session['username'])


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=)
