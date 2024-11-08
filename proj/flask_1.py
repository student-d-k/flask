from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def home():
    return 'Hello, World!'


@app.route('/2')
def f2():
    return 'Hello, World 2!'


@app.route('/3<name>')
def f3(name):
    return f'Hello {name}!'


@app.route('/4')
def f4():
    return render_template('4.html', names = ['Alice', 'Bob', 'Charlie'])


if __name__ == '__main__':
    app.run(debug=True)
