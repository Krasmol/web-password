from flask import Flask, render_template, request
import random
import string

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
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

if __name__ == '__main__':
    app.run(debug=True)
