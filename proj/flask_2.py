from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Sample users dictionary for demo purposes
users = {"admin": "password"}

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            return redirect(url_for('welcome', username=username))
        else:
            return "Invalid username or password"
    return render_template('login.html')

@app.route('/welcome/<username>')
def welcome(username):
    return f"Welcome, {username}!"

if __name__ == "__main__":
    app.run(debug=True)
