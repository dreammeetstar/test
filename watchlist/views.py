from flask import render_template, url_for, request, flash, redirect
from markupsafe import escape
from flask_login import login_user, login_required, logout_user, current_user
from watchlist import app, db
from watchlist.models import User, Movie, GiveSay
import time


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':  # 判断是否是 POST 请求
        if not current_user.is_authenticated:  # 如果当前用户未认证
            return redirect(url_for('index'))  # 重定向到主页
        # 获取表单数据
        title = request.form.get('title')  # 传入表单对应输入字段的 name 值
        year = request.form.get('year')
        # 验证数据
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')  # 显示错误提示
            return redirect(url_for('index'))  # 重定向回主页
        # 保存表单数据到数据库
        movie = Movie(title=title, year=year)  # 创建记录
        db.session.add(movie)  # 添加到数据库会话
        db.session.commit()  # 提交数据库会话
        flash('Item created.')  # 显示成功创建的提示
        return redirect(url_for('index'))  # 重定向回主页

    movies = Movie.query.all()
    return render_template('index.html', movies=movies)

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

@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':  # 处理编辑表单的提交请求
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))  # 重定向回对应的编辑页面

        movie.title = title  # 更新标题
        movie.year = year  # 更新年份
        db.session.commit()  # 提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index'))  # 重定向回主页

    return render_template('edit.html', movie=movie)  # 传入被编辑的电影记录

@app.route('/movie/delete/<int:movie_id>', methods=['POST'])  # 限定只接受 POST 请求
@login_required  # 登录保护
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)  # 获取电影记录
    db.session.delete(movie)  # 删除对应的记录
    db.session.commit()  # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('index'))  # 重定向回主页

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()
        # 验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user)  # 登入用户
            flash('Login success.')
            return redirect(url_for('index'))  # 重定向到主页

        flash('Invalid username or password.')  # 如果验证失败，显示错误消息
        return redirect(url_for('login'))  # 重定向回登录页面

    return render_template('login.html')

@app.route('/logout')
@login_required  # 用于视图保护，后面会详细介绍
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.')
    return redirect(url_for('index'))  # 重定向回首页

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')

@app.route('/givesay', methods=['GET', 'POST'])
def givesay():
    if request.method == 'POST':
        name = request.form['name']
        content = request.form['content']
        img = request.form['img']
        createTime = round(time.time())
        if not name or not content or len(name) > 120 or len(content) > 900:
            flash('Invalid input.')
            return redirect(url_for('givesay'))
        say = GiveSay(name=name, content=content, img=img, createTime=createTime)
        db.session.add(say)
        db.session.commit()
        flash('Give say success.')
        return redirect(url_for('givesay'))

    if current_user.is_authenticated:
        GiveSayUser = current_user
    else:
        GiveSayUser = ''
    import requests, json
    res = requests.get('https://raw.githubusercontent.com/FarEastSea/schedule/master/Zone/result.txt')
    restext = json.loads(res.text)
    sayList = GiveSay.query.all()
    sayList.extend(restext)
    # if say['img'] is defined 提供一种思路，这是用在jinja2里的，python里可以判断是否为None
    sayList.sort(key=lambda x: x['createTime'] if isinstance(x, dict) else x.createTime, reverse=True)
    return render_template('givesay.html', GiveSayUser=GiveSayUser, sayList=sayList)

@app.route('/checktext', methods=['GET'])
def checktext():
    return render_template('checktext.html')
