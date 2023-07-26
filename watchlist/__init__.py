import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


WIN = sys.platform.startswith("win")
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app = Flask(__name__)
# 等同于 app.secret_key = 'dev'
app.config['SECRET_KEY'] = 'dev'
# 注意更新这里的路径，把 app.root_path 添加到 os.path.dirname() 中
# 以便把文件定位到项目根目录
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), 'data.db')
# 关闭对模型修改的监控
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 在扩展类实例化前加载配置
# 实例化扩展类
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# 创建用户加载回调函数，接受用户 ID 作为参数
@login_manager.user_loader
def load_user(user_id):
    from watchlist.models import User
    user = User.query.get(int(user_id))           # 用 ID 作为 User 模型的主键查询对应的用户
    return user                                   # 返回用户对象

# 重定向操作
login_manager.login_view = 'login'
# 自定义错误提示消息
# login_manager.login_message = ''

# 模板上下文处理函数
@app.context_processor
def inject_user():
    from watchlist.models import User
    user = User.query.first()
    return dict(user=user)


from watchlist import views, errors, commands
from watchlist.models import User, Movie
