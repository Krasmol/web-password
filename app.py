from flask import Flask, render_template, request
import random
import string

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def generator():
    passwords = []

    if request.method == 'POST':
        length = int(request.form.get('length', 12))
        for _ in range(5):
            chars = string.ascii_letters + string.digits + "!@#$%"
            password = ''.join(random.choice(chars) for _ in range(length))
            passwords.append(password)

    return render_template('generator.html', passwords=passwords)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
