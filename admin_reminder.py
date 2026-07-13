import os
from flask import Flask, request, jsonify, session, redirect
from datetime import timedelta,datetime

app = Flask(__name__)

#登录逻辑
app.secret_key = os.environ.get("SECRET_KEY", "local-test-key")
app.config["SESSION_PERMANENT"] = False
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD","123456")
app.permanent_session_lifetime = timedelta(minutes=30)

devices = {}
#默认无操作提醒时间
idle_limit_minutes = 15
# 工作时间配置
work_start_time = "09:00"
work_end_time = "18:00"

# 工作日（周一到周五）
work_days = [0,1,2,3,4]

@app.before_request
def check_login():
    #打印结果
    #print("访问:", request.path, "登录状态:", session.get("logged_in"))
    if request.endpoint in [
        "login",
        "static",
        "report",
        "config",
        "warning_confirm"]:
        return

    if not session.get("logged_in"):
        return redirect("/login")

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == "POST":
        password = request.form.get("password")

        if password == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect("/")

        return "密码错误"

    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>管理员登录</title>

    <style>
        body {
            margin: 0;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #667eea, #764ba2);
            font-family: "Microsoft YaHei", Arial, sans-serif;
        }

        .login-box {
            width: 360px;
            padding: 40px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            text-align: center;
        }

        .logo {
            font-size: 42px;
            margin-bottom: 15px;
        }

        h2 {
            margin-bottom: 30px;
            color: #333;
            font-weight: 600;
        }

        input {
            width: 100%;
            height: 45px;
            padding: 0 15px;
            box-sizing: border-box;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            outline: none;
            transition: 0.3s;
        }

        input:focus {
            border-color: #667eea;
            box-shadow: 0 0 8px rgba(102,126,234,0.3);
        }

        button {
            margin-top: 25px;
            width: 100%;
            height: 45px;
            border: none;
            border-radius: 8px;
            background: #667eea;
            color: white;
            font-size: 16px;
            cursor: pointer;
            transition: 0.3s;
        }

        button:hover {
            background: #5568d3;
        }

        .footer {
            margin-top: 25px;
            font-size: 13px;
            color: #999;
        }
    </style>

    </head>

    <body>

    <div class="login-box">

        <div class="logo">🔐</div>

        <h2>管理员登录</h2>

        <form method="post">

            <input 
                type="password" 
                name="password" 
                placeholder="请输入管理员密码"
                required
            >

            <button type="submit">
                登录
            </button>

        </form>

        <div class="footer">
            Reminder Management System
        </div>

    </div>

    </body>
    </html>
    """
#

@app.route('/setting', methods=['GET', 'POST'])
def setting():

    global idle_limit_minutes

    if request.method == "POST":
        value = request.form.get("minutes")

        idle_limit_minutes = int(value)

    html = f"""
<html>
<head>
    <meta charset="utf-8">
    <title>无操作提醒设置</title>
<style>
    body {{
    margin:0;
    padding:30px;
    background:#f5f7fb;
    font-family:
    "Microsoft YaHei",
    Arial,
    sans-serif;
    }}
    .container {{

    max-width:600px;

    margin:auto;
   }}
   
    .title {{

    font-size:28px;

    font-weight:bold;

    color:#1f2937;

    margin-bottom:25px;

    }}
    .card {{

    background:white;

    padding:30px;

    border-radius:12px;

    box-shadow:
    0 3px 10px rgba(0,0,0,0.05);

    }}
    .label {{

    font-size:16px;

    color:#374151;

    margin-bottom:10px;

    display:block;

    
    }}
    input {{
    width:100%;
    box-sizing:border-box;
    padding:12px;
    font-size:16px;
    border-radius:8px;
    border:1px solid #d1d5db;
    margin-bottom:20px;
    }}
    button {{
    width:100%;
    padding:12px;
    border:none;
    border-radius:8px;
    background:#1B4388;
    color:white;
    font-size:16px;
    cursor:pointer;
    }}
    button:hover {{
    background:#16366d;
    }}
    .info {{
    margin-top:20px;
    padding:15px;
    background:#f3f4f6;
    border-radius:8px;
    color:#4b5563;
    }}
   </style>
</head>
<body>
<div class="container">
<div class="title">
无操作提醒设置
</div>
<div class="card">
<form method="post">
<label class="label">
多少分钟无操作后提醒：
</label>
<input type="number" name="minutes" min="1" max="999" value="{idle_limit_minutes}">
<button type="submit">
保存设置
</button>
</form>
<div class="info">
当前设置：电脑连续无操作 
<b>{idle_limit_minutes}</b>分钟后触发提醒。
</div>
</div>
</div>
</body>
</html>
"""
    return html

@app.route('/config')
def config():

    return jsonify({
        "idle_limit_minutes": idle_limit_minutes,

        "work_start_time": work_start_time,

        "work_end_time": work_end_time,

        "work_days": work_days

    })

@app.route('/report', methods=['POST'])
def report():
    data = request.json
    #print测试客户端返回的数据
    #print("收到客户端数据:", data)
    pc = data.get("pc")
    user = data.get("user")
    ip = data.get("ip")
    idle = data.get("idle")
    idle_minutes = data.get("idle_minutes")
    popup_time = data.get("popup_time")
    timestamp = data.get("timestamp")
    # 客户端弹窗时间（如果客户端有发送）
    now = datetime.now()

    if pc not in devices:
        devices[pc] = {
            "user": user,
            "ip": ip,
            "idle": 0,
            "status": "在线",
            "time": timestamp,

            "idle_start": None,
            "last_idle_duration": "0分钟",
            "last_popup_time": "-"
        }

    device = devices[pc]
    # 更新基础信息
    device["user"] = user
    device["ip"] = ip
    device["time"] = timestamp
    # =====================
    # 当前进入无操作
    # =====================
    if idle == 1:

        # 之前是在线，现在变无操作
        if device["idle"] == 0:

            device["idle_start"] = now

            # 记录弹窗时间
            if popup_time:
                device["last_popup_time"] = popup_time

        device["status"] = "无操作"
        # =====================
        # 当前有人操作
        # =====================
    else:

        # 之前是无操作，现在恢复
        if device["idle"] == 1:

            if device["idle_start"]:
                duration = now - device["idle_start"]

                minutes = int(
                    duration.total_seconds() / 60
                )

                device["last_idle_duration"] = f"{minutes}分钟"

        device["status"] = "在线"
        # 保存当前状态
    device["idle"] = idle

    return jsonify({
        "status": "ok"
    })

#关闭弹窗后返回提醒时间
@app.route('/warning_confirm', methods=['POST'])
def warning_confirm():

    data = request.json

    pc = data.get("pc")


    if pc not in devices:
        devices[pc] = {}


    devices[pc]["last_idle"] = data.get("idle")

    devices[pc]["last_warning_time"] = data.get("timestamp")


    return jsonify({
        "status":"ok"
    })

@app.route('/')
def index():
    total = len(devices)
    online = 0
    away = 0
    for pc, v in devices.items():

        if v["idle"] == 1:
            away += 1
        else:
            online += 1
    html = """
<!DOCTYPE html>
<html>
<head>

<meta charset="utf-8">

<title>员工居家办公状态</title>

<meta http-equiv="refresh" content="30">

<style>

body {

    margin:0;
    padding:30px;
    background:#f5f7fb;
    font-family:
    "Microsoft YaHei",
    Arial,
    sans-serif;

}


.container {

    max-width:1200px;

    margin:auto;

}


.title {

    font-size:28px;

    font-weight:bold;

    margin-bottom:25px;

    color:#1f2937;

}


/* 数据卡片 */

.cards {

    display:flex;

    gap:20px;

    margin-bottom:30px;

}


.card {

    background:white;

    padding:20px;

    border-radius:12px;

    flex:1;

    box-shadow:
    0 3px 10px rgba(0,0,0,0.05);

}


.card h3 {

    margin:0;

    color:#6b7280;

    font-size:14px;

}


.card p {

    margin-top:10px;

    font-size:30px;

    font-weight:bold;

}


/* 表格 */


.table-box {

    background:white;

    border-radius:12px;

    padding:20px;

    box-shadow:
    0 3px 10px rgba(0,0,0,0.05);

}


table {

    width:100%;

    border-collapse:collapse;

}


th {

    background:#f3f4f6;

    padding:14px;

    text-align:left;

    color:#374151;

}


td {

    padding:14px;

    border-bottom:
    1px solid #eee;

}


tr:hover {

    background:#f9fafb;

}


/* 状态 */


.normal {

    color:#16a34a;

    font-weight:bold;

}

.away {

    color:#dc2626;

    font-weight:bold;

}
</style>
</head>
<body>
<div class="container">
<div class="title">
员工居家办公实时状态
</div>
<div class="cards">
<div class="card">

<h3>设备总数</h3>

<p>
""" + str(total) + """
</p>

</div>
<div class="card">

<h3>当前在线</h3>

<p style="color:#16a34a">

""" + str(online) + """

</p>
</div>
<div class="card">

<h3>当前无操作</h3>

<p style="color:#dc2626">

""" + str(away) + """

</p>
</div>
</div>
<div class="table-box">
<table>
<tr>
<th>电脑</th>
<th>用户</th>
<th>IP</th>
<th>电脑状态</th>
<th>最近一次无操作时长</th>
<th>最近一次提醒</th>

</tr>

"""
    #当前这台电脑现在有没有超过无操作时间。
    # 输出设备列表
    for pc, v in devices.items():
       if v["idle"] == 1:
            status = """
<span class="away">
无操作
</span>
"""
       else:
           status = """
<span class="normal">
在线
</span>
"""

       html += f"""

<tr>

<td>{pc}</td>

<td>{v['user']}</td>

<td>{v['ip']}</td>

<td>{status}</td>

<td>
{v.get('last_idle_duration','-')}
</td>

<td>
{v.get('last_popup_time','-')}
</td>

</tr>

"""
    html += """
</table>
</div>
</div>

</body>
</html>

"""

    return html


if __name__ == "__main__":
    app.run(
       host="0.0.0.0",
       port=int(os.environ.get("PORT",5000))
    )
