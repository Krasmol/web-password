from flask import Flask, render_template, request
import secrets
import string

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def password_generator():
    passwords_list = []
    
    if request.method == 'POST':
        size = int(request.form.get('size', 14))
        
        # Создаем 5 паролей
        for i in range(5):
            characters = string.ascii_letters + string.digits + "!@#$%&*"
            secure_password = ''.join(secrets.choice(characters) for _ in range(size))
            passwords_list.append(secure_password)
    
    return render_template('generator.html', passwords_list=passwords_list)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
