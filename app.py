from flask import Flask, render_template, request, redirect, url_for, session
import random
import string
import time

app = Flask(__name__)
app.secret_key = 'secret'

USERNAME = 'admin'
PASSWORD = '12345'

failed_attempts = {}


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    user_ip = request.remote_addr

    if user_ip not in failed_attempts:
        failed_attempts[user_ip] = 0

    captcha_required = failed_attempts[user_ip] >= 3
    if captcha_required and 'captcha_answer' not in session:
        generate_crazy_captcha()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if captcha_required:
            user_captcha = request.form.get('captcha', '')
            if str(user_captcha).lower() != str(session.get('captcha_answer', '')).lower():
                failed_attempts[user_ip] += 1
                generate_crazy_captcha()
                return render_template('login.html',
                                       error="НЕПРАВИЛЬНАЯ КАПЧА! 🚨",
                                       captcha_required=True,
                                       captcha_text=session.get('captcha_text', ''),
                                       failed_attempts=failed_attempts[user_ip])

        if username == USERNAME and password == PASSWORD:
            failed_attempts[user_ip] = 0
            session['user'] = username
            print(f"Привет, {session['user']})! Это ваш личный кабинет")
            return redirect(url_for('generator'))
        else:
            failed_attempts[user_ip] += 1
            error_msg = "Неверный логин или пароль"

            if failed_attempts[user_ip] >= 3:
                error_msg = f"🚨 АТАКА ОБНАРУЖЕНА! Введите капчу! 🚨 (Попытка: {failed_attempts[user_ip]})"
                generate_crazy_captcha()

            return render_template('login.html',
                                   error=error_msg,
                                   captcha_required=failed_attempts[user_ip] >= 3,
                                   captcha_text=session.get('captcha_text', ''),
                                   failed_attempts=failed_attempts[user_ip])

    return render_template('login.html',
                           captcha_required=captcha_required,
                           captcha_text=session.get('captcha_text', ''),
                           failed_attempts=failed_attempts[user_ip])


def generate_crazy_captcha():
    """Генерирует безумную капчу"""
    captcha_types = [

        lambda: {
            'text': f"{random.randint(10, 50)} + {random.randint(10, 50)} - {random.randint(1, 20)}",
            'answer': str(eval(f"{random.randint(10, 50)} + {random.randint(10, 50)} - {random.randint(1, 20)}"))
        },

        lambda: {
            'text': f"Сколько букв в слове '{random.choice(['КРАСНЫЙ', 'ЗЕЛЕНЫЙ', 'СИНИЙ', 'ЖЕЛТЫЙ', 'ФИОЛЕТОВЫЙ'])}'?",
            'answer': str(len(random.choice(['КРАСНЫЙ', 'ЗЕЛЕНЫЙ', 'СИНИЙ', 'ЖЕЛТЫЙ', 'ФИОЛЕТОВЫЙ'])))
        },

        lambda: {
            'text': f"Сколько {random.choice(['🐱', '🐶', '🐵', '🐯', '🐻'])} здесь: {' '.join([random.choice(['🐱', '🐶', '🐵', '🐯', '🐻'])] * random.randint(3, 7))}",
            'answer': str(random.randint(3, 7))
        },

        lambda: {
            'text': f"Напишите число {random.randint(100, 999)} задом наперед",
            'answer': str(random.randint(100, 999))[::-1]
        },

        lambda: {
            'text': f"Сколько часов в {random.randint(2, 6)} днях?",
            'answer': str(random.randint(2, 6) * 24)
        },

        lambda: {
            'text': f"Напишите первую букву слова '{random.choice(['ПАРОЛЬ', 'КОМПЬЮТЕР', 'ПРОГРАММА', 'СЕРВЕР', 'БРАУЗЕР'])}'",
            'answer': random.choice(['ПАРОЛЬ', 'КОМПЬЮТЕР', 'ПРОГРАММА', 'СЕРВЕР', 'БРАУЗЕР'])[0]
        },

        lambda: {
            'text': f"Решите: {random.randint(2, 5)} * {random.randint(2, 5)} + {random.randint(1, 10)}",
            'answer': str(random.randint(2, 5) * random.randint(2, 5) + random.randint(1, 10))
        }
    ]

    captcha = random.choice(captcha_types)()
    session['captcha_text'] = captcha['text']
    session['captcha_answer'] = captcha['answer']
    session['captcha_generated_at'] = time.time()


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


@app.route('/generator', methods=['GET', 'POST'])
def generator():
    if 'user' not in session:
        return redirect(url_for('login'))

    passwords = []

    if request.method == 'POST':
        length = int(request.form.get('length', 12))
        for _ in range(5):
            chars = string.ascii_letters + string.digits + "!@#$%"
            password = ''.join(random.choice(chars) for _ in range(length))
            passwords.append(password)

    return render_template('generator.html', passwords=passwords, user=session['user'])


if __name__ == '__main__':
    app.run(debug=True,)
