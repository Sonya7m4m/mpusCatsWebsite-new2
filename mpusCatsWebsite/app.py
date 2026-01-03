import os
# 新增这行：强制声明Flask入口文件
os.environ['FLASK_APP'] = 'app.py'

from flask import Flask, render_template, request, redirect, flash, url_for
import json
from datetime import datetime
from werkzeug.utils import secure_filename

# 初始化Flask应用
app = Flask(__name__)
app.secret_key = 'campus_cat_123456'
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # 匹配你的static/uploads路径
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 限制5MB上传文件

# 创建上传文件夹（确保Vercel环境也能创建）
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 数据持久化相关配置
DATA_FILE = 'cat_data.json'


# 加载猫咪和评论数据
def load_data():
    """从JSON文件加载数据，无文件则初始化默认数据"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('cats', []), data.get('comments', [])
        except:
            # 读取失败则初始化默认数据
            pass

    # 初始化默认猫咪数据（修正location拼写错误）
    init_cats = [
        {"id": 1, "name": "海参", "personality": "温顺", "location": "操场边", "img": "cat1.jpg"},
        {"id": 2, "name": "朵朵", "personality": "粘人", "location": "食堂门口", "img": "cat2.jpg"},
        {"id": 3, "name": "温初实", "personality": "高冷", "location": "操场边", "img": "cat3.jpg"},
        {"id": 4, "name": "嘎嘎", "personality": "胆小", "location": "二饭门口", "img": "cat4.jpg"},
        {"id": 5, "name": "小灰", "personality": "懒", "location": "操场边", "img": "cat5.jpg"},
        {"id": 6, "name": "罐罐", "personality": "贪吃", "location": "饭堂后面", "img": "cat6.jpg"},
        {"id": 7, "name": "柿子", "personality": "生人勿近", "location": "B栋行政楼后", "img": "cat7.jpg"}
    ]
    # 初始化默认评论数据
    init_comments = [
        {"id": 1, "cat_id": 1, "content": "好乖的橘猫！每天都在图书馆旁看到它", "img": "", "time": "2026-01-02 10:00"},
        {"id": 2, "cat_id": 1, "content": "喂过它一次小鱼干，超亲人～", "img": "", "time": "2026-01-02 11:30"}
    ]
    save_data(init_cats, init_comments)
    return init_cats, init_comments


def save_data(cats, comments):
    """保存数据到JSON文件"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({"cats": cats, "comments": comments}, f, ensure_ascii=False, indent=2)


# 加载初始数据
cats, comments = load_data()


# 检查文件格式是否合法
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# 首页路由（核心根路由，解决404）
@app.route('/')
def index():
    return render_template('index.html', cats=cats)


# 猫咪详情页
@app.route('/detail/<int:cat_id>')
def cat_detail(cat_id):
    cat = next((c for c in cats if c['id'] == cat_id), None)
    if not cat:
        flash('猫咪不存在！')
        return redirect(url_for('index'))
    cat_comments = [cmt for cmt in comments if cmt['cat_id'] == cat_id]
    return render_template('cat_detail.html', cat=cat, comments=cat_comments)


# 提交评论（支持图片上传）
@app.route('/add_comment/<int:cat_id>', methods=['POST'])
def add_comment(cat_id):
    content = request.form.get('content', '').strip()
    if not content:
        flash('评论内容不能为空！')
        return redirect(url_for('cat_detail', cat_id=cat_id))

    # 处理评论图片上传
    img_filename = ''
    if 'comment_img' in request.files:
        file = request.files['comment_img']
        if file and allowed_file(file.filename):
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            safe_name = secure_filename(file.filename)
            img_filename = f"comment_{cat_id}_{timestamp}_{safe_name}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))

    # 新增评论
    new_comment = {
        "id": len(comments) + 1,
        "cat_id": cat_id,
        "content": content,
        "img": img_filename,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    comments.append(new_comment)
    save_data(cats, comments)
    flash('评论发布成功！')
    return redirect(url_for('cat_detail', cat_id=cat_id))


# 新增猫咪
@app.route('/add_cat', methods=['GET', 'POST'])
def add_cat():
    if request.method == 'POST':
        # 表单校验
        name = request.form.get('name', '').strip()
        personality = request.form.get('personality', '').strip()
        location = request.form.get('location', '').strip()
        if not (name and personality and location):
            flash('名称、性格、位置不能为空！')
            return redirect(url_for('add_cat'))

        # 处理猫咪图片上传
        img_filename = ''
        if 'cat_img' in request.files:
            file = request.files['cat_img']
            if file and allowed_file(file.filename):
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                safe_name = secure_filename(file.filename)
                img_filename = f"cat_{len(cats) + 1}_{timestamp}_{safe_name}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))

        # 新增猫咪数据
        new_cat = {
            "id": len(cats) + 1,
            "name": name,
            "gender": request.form.get('gender', ''),
            "personality": personality,
            "location": location,
            "img": img_filename
        }
        cats.append(new_cat)
        save_data(cats, comments)
        flash('猫咪新增成功！')
        return redirect(url_for('index'))
    return render_template('add_cat.html')


# 编辑猫咪
@app.route('/edit_cat/<int:cat_id>', methods=['GET', 'POST'])
def edit_cat(cat_id):
    cat = next((c for c in cats if c['id'] == cat_id), None)
    if not cat:
        flash('猫咪不存在！')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # 表单校验
        name = request.form.get('name', '').strip()
        personality = request.form.get('personality', '').strip()
        location = request.form.get('location', '').strip()
        if not (name and personality and location):
            flash('名称、性格、位置不能为空！')
            return redirect(url_for('edit_cat', cat_id=cat_id))

        # 处理图片上传（可选）
        img_filename = cat['img']
        if 'cat_img' in request.files:
            file = request.files['cat_img']
            if file and allowed_file(file.filename):
                # 删除原图片
                if img_filename and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], img_filename)):
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
                # 保存新图片
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                safe_name = secure_filename(file.filename)
                img_filename = f"cat_{cat_id}_{timestamp}_{safe_name}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))

        # 更新猫咪信息
        cat['name'] = name
        cat['gender'] = request.form.get('gender', '')
        cat['personality'] = personality
        cat['location'] = location
        cat['img'] = img_filename

        save_data(cats, comments)
        flash('猫咪信息编辑成功！')
        return redirect(url_for('index'))

    return render_template('edit_cat.html', cat=cat)


# 删除猫咪
@app.route('/delete_cat/<int:cat_id>')
def delete_cat(cat_id):
    global cats
    # 查找猫咪
    cat = next((c for c in cats if c['id'] == cat_id), None)
    if not cat:
        flash('猫咪不存在！')
        return redirect(url_for('index'))

    # 删除关联图片
    if cat['img'] and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], cat['img'])):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], cat['img']))

    # 删除猫咪和关联评论
    cats = [c for c in cats if c['id'] != cat_id]
    global comments
    comments = [cmt for cmt in comments if cmt['cat_id'] != cat_id]

    save_data(cats, comments)
    flash('猫咪删除成功！')
    return redirect(url_for('index'))


# 本地运行入口
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)


# ===== Vercel Serverless 核心入口（必须保留）=====
def handler(event, context):
    from werkzeug.middleware.dispatcher import DispatcherMiddleware

    return DispatcherMiddleware(app).wsgi_app(event, context)
