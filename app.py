from flask import Flask, render_template, url_for, request
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/students'

@app.route('/')
def home():
    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        return render_template('register.html')
    else:
        return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        return render_template('login.html')
    else:
        return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True)
