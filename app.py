import time
import threading
import requests
import random
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Proxy Settings
PROXY_BASE = "https://long-sound-d421.boorapolat.workers.dev"
tasks = {}

def get_discord_user(token):
    url = f"{PROXY_BASE}/api/v9/users/@me"
    headers = {"Authorization": token}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

def sender_thread(task_id, token, channels, message, interval, jitter, auto_delete):
    channel_list = [c.strip() for c in channels.split(',') if c.strip()]
    while tasks.get(task_id, False):
        for ch_id in channel_list:
            if not tasks.get(task_id): break
            url = f"{PROXY_BASE}/api/v9/channels/{ch_id}/messages"
            headers = {"Authorization": token, "Content-Type": "application/json"}
            try:
                r = requests.post(url, json={"content": message}, headers=headers)
                if r.status_code == 200 and auto_delete:
                    msg_id = r.json().get('id')
                    time.sleep(1.2)
                    requests.delete(f"{url}/{msg_id}", headers=headers)
            except:
                pass
        wait = float(interval)
        if jitter: wait += random.uniform(0.1, 1.5)
        time.sleep(max(0.5, wait))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/validate', methods=['POST'])
def validate():
    token = request.json.get('token')
    user = get_discord_user(token)
    if user:
        return jsonify({"success": True, "username": user['username']})
    return jsonify({"success": False}), 401

@app.route('/api/start', methods=['POST'])
def start():
    active_count = sum(1 for status in tasks.values() if status is True)
    if active_count >= 2:
        return jsonify({"success": False, "message": "Campaign limit reached (Max 2)."}), 400
    
    data = request.json
    t_id = data.get('id', 'Task_1')
    tasks[t_id] = True
    
    thread = threading.Thread(target=sender_thread, args=(
        t_id, data['token'], data['channels'], data['message'],
        data['interval'], data['jitter'], data['auto_delete']
    ))
    thread.daemon = True
    thread.start()
    return jsonify({"success": True})

@app.route('/api/stop', methods=['POST'])
def stop():
    t_id = request.json.get('id')
    tasks[t_id] = False
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

