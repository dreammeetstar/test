from flask import Flask
from markupsafe import escape
from flask import url_for

app = Flask(__name__)

@app.route('/')
def hello():
    return "<h1>Welcome!</h1>"

@app.route('/user/<name>')
def user_page(name):
	return f"<h1>Welcome to My Test!</h1><div>hello!{escape(name)}</div><img src='http://helloflask.com/totoro.gif'>"

@app.route("/test")
def test():
    print(url_for('hello'))
    print(url_for('user_page',name='123'))
    print(url_for('test'))
    print(url_for('test',name='12'))
    return '什么？！！'
