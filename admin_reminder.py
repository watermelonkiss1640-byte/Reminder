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
idle_limit_minutes = 20
# 工作时间配置
work_start_time = "09:00"
work_end_time = "18:00"

# 工作日（周一到周五）
work_days = [0,1,2,3,4]

@app.before_request
def check_login():
    if request.path in [
        "/login",
        "/report",
        "/config",
        "/static/favicon.ico",
        "/warning_confirm",
        "/popup_show",

    ]:
        return

    if not session.get("logged_in"):
        return redirect("/login")


@app.route('/warning_confirm', methods=['POST'])
def warning_confirm():

    data=request.json

    pc=data.get("pc")

    if pc in devices:

        devices[pc]["alert_showing"]=False
        #清理旧的弹窗时间
        devices[pc]["alert_start_time"] = None

        devices[pc]["idle_start_time"]=datetime.utcnow()+timedelta(hours=8)

        devices[pc]["status"] = "在线"
        print(
            "确认关闭后:",
            pc,
            "alert_showing:",
            devices[pc]["alert_showing"],
            "alert_start_time:",
            devices[pc]["alert_start_time"]
        )

    return jsonify({
        "status":"ok"
    })

@app.route("/popup_show", methods=["POST"])
def popup_show():

    data = request.json

    pc = data.get("pc")

    device = devices.get(pc)
    if not device:
        return jsonify({
            "status": "error",
            "message": "device not found"
        })

    if device:

        now = datetime.utcnow() + timedelta(hours=8)
        # 最近一次弹窗时间
        device["last_popup_time"] = (
            now.strftime("%Y-%m-%d %H:%M:%S")
        )

        # 每天提醒次数清零
        today = now.date()

        if device["popup_date"] != today:

            device["popup_date"] = today
            device["today_popup_count"] = 0

        # 弹窗次数+1
        device["today_popup_count"] += 1
        # 更新设备状态
        device["status"] = "提醒中"
        #第一次进入提醒状态的时间
        if not device.get("alert_showing"):
            device["alert_start_time"] = now

        # 标记弹窗存在
        device["alert_showing"] = True

    # print(
    #     "弹窗记录:",
    #     pc,
    #     device["last_popup_time"],
    #     device["today_popup_count"],
    #     "popup_show更新后:",
    #     device["status"],
    #     device["alert_showing"]
    # )
    return jsonify({
            "status": "ok",
            "last_popup_time": device["last_popup_time"],
            "today_popup_count": device["today_popup_count"],
            "device_status": device["status"]
    })

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

        "lunch_start_time": "12:00",

        "lunch_end_time": "13:00",

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
    idle_minutes = data.get("idle_minutes", 0)
    alert_closed = data.get("alert_closed")
    timestamp = data.get("timestamp")

    # 客户端弹窗时间（如果客户端有发送）
    now = datetime.utcnow() + timedelta(hours=8)

    if pc not in devices:
        devices[pc] = {
            "user": user,
            "ip": ip,
            "idle": idle,
            "status": "在线",
            "time": timestamp,
            "last_report_time": now,
            # 最近一次提醒时间
            "last_popup_time": "-",
            # 今日提醒次数
            "today_popup_count": 0,
            # 记录提醒日期，用于每天自动清零
            "popup_date": now.date(),
            "alert_closed": True,
            "alert_required": False,
            #弹窗开始的时间
            "idle_start_time":"-",
            #弹窗出现
            "alert_showing": False,
            #当前提醒开始时间
            "alert_start_time": None

        }
    device = devices[pc]
    # 用户关闭提醒
    if alert_closed:
        device["alert_closed"] = True
    # 更新基础信息
    device["user"] = user
    device["ip"] = ip
    device["time"] = timestamp
    device["last_report_time"] = now
    device["idle"] = idle
    device["idle_minutes"] = idle_minutes
    device["idle_start_time"] = data.get(
        "idle_start_time"
    )

    # =====================
    # 判断是否需要提醒
    # =====================

    show_alert = False
    # 当前时间
    now_check = now

    current_work_time = False
    # 判断是否工作日
    if now_check.weekday() in work_days:

        current = now_check.strftime("%H:%M")

        # 上午 09:00 - 12:00
        if (
                work_start_time <= current < "12:00"
        ):
            current_work_time = True


        # 下午 13:00 - 18:00
        elif (
                "13:00" <= current < work_end_time
        ):
            current_work_time = True

    print(
        "工作时间判断:",
        current_work_time,
        "当前时间:",
        now_check.strftime("%Y-%m-%d %H:%M")
    )

    # =====================
    # 判断是否需要提醒
    # =====================
    # 只有工作时间才判断空闲
    if current_work_time:

        if idle_minutes >= idle_limit_minutes:

            # 当前没有弹窗
            if not device["alert_showing"]:
                show_alert = True

                device["alert_required"] = True

        else:

            device["alert_required"] = False

    else:

        # 非工作时间，不触发提醒

        device["alert_required"] = False

    print(
            "设备状态:",
            pc,
            "idle:",
            idle_minutes,
            "alert_showing:",
            device["alert_showing"],
            "show_alert:",
            show_alert,
            "alert_required",
            device["alert_required"]
    )

    return jsonify({
         "status": "ok",
         # 告诉客户端现在是否需要弹窗
         "show_alert": show_alert,
         # 服务器认定的空闲分钟
         "server_idle_minutes": idle_minutes,
         # 客户端是否已经显示弹窗
         "alert_showing": device["alert_showing"],
        #弹窗出现的时间
        "alert_start_time": device["alert_start_time"],
        "alert_required": device["alert_required"]
    })

@app.route('/')
def index():
    now = datetime.utcnow() + timedelta(hours=8)
    # 清理超过7天没有心跳的设备
    remove_list = []

    for pc, v in devices.items():

        if now - v["last_report_time"] > timedelta(days=7):
            remove_list.append(pc)

    for pc in remove_list:
        del devices[pc]

    total = len(devices)

    online = 0
    away = 0
    offline = 0

    for pc, v in devices.items():

        # 弹窗出现30分钟，没有返回关闭
        if v.get("alert_showing"):

            alert_start_time = v.get(
                "alert_start_time"
            )

            if (
                    alert_start_time
                    and now - alert_start_time > timedelta(minutes=30)
            ):
                v["status"] = "休眠"
                offline += 1
                print(
                    "进入休眠状态:",
                    pc,
                    "alert_start_time:",
                    alert_start_time,
                    "当前时间:",
                    now,
                    "持续时间:",
                    now - alert_start_time
            )
            # 已经弹窗提醒，等待员工确认
            else:

                v["status"] = "提醒中"
                away += 1

        # 正常在线
        else:

            v["status"] = "在线"
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
<div style="
        margin-top:12px;
        color:#dc2626;
        font-size:14px;
        font-weight:bold;
    ">
        备注：仅记录工作日 09:00-12:00、13:00-18:00 的电脑状态。
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

<h3>电脑休眠</h3>

<p style="color:#dc2626">

""" + str(offline) + """

</p>
</div>
<div class="card">

<h3>办公提醒中</h3>

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
<th>最近一次办公提醒</th>
<th>今日提醒次数</th>
</tr>

"""
    #当前这台电脑现在有没有超过无操作时间。
    # 输出设备列表
    for pc, v in devices.items():
        if v.get("status") == "休眠":

            status = """
       <span class="away">
       无人响应
       </span>
       """

        elif v.get("status") == "提醒中":

            status = """
       <span class="away">
       提醒中
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
        {v.get('last_popup_time','-')}
        </td>
        <td>
        {v.get('today_popup_count',0)}
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
