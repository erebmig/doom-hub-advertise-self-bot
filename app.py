import time
import threading
import requests
import random
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Task storage
tasks = {}

# [span_3](start_span)ProxyScrape Premium HTTP Listesi[span_3](end_span)
PREMIUM_PROXIES = [
    "65.111.4.42:3129", "65.111.4.231:3129", "209.50.176.47:3129", "209.50.190.148:3129",
    "65.111.13.240:3129", "216.26.233.38:3129", "216.26.237.3:3129", "209.50.170.113:3129",
    "216.26.249.39:3129", "104.207.61.41:3129", "45.3.52.108:3129", "65.111.4.9:3129",
    "104.207.59.148:3129", "209.50.164.249:3129", "216.26.253.9:3129", "217.181.90.16:3129",
    "216.26.230.41:3129", "104.207.63.133:3129", "104.207.41.26:3129", "216.26.252.79:3129",
    "216.26.242.129:3129", "104.167.19.219:3129", "45.3.38.73:3129", "65.111.24.212:3129",
    "216.26.232.208:3129", "45.3.38.91:3129", "216.26.248.211:3129", "216.26.250.242:3129",
    "216.26.248.46:3129", "104.207.61.253:3129", "209.50.160.59:3129", "65.111.31.253:3129"
    # [span_4](start_span)Liste devam ediyor... Tümünü koda ekleyebilirsin[span_4](end_span)
]

def get_random_proxy():
    [span_5](start_span)"""Listeden rastgele bir proxy objesi döndürür[span_5](end_span)."""
    p = random.choice(PREMIUM_PROXIES)
    return {
        "http": f"http://{p}",
        "https": f"http://{p}"
    }

def get_discord_user(token):
    [span_6](start_span)"""Token kontrolünü rastgele bir premium proxy ile yapar[span_6](end_span)."""
    for _ in range(3): # 3 farklı proxy deneme hakkı
        try:
            proxy = get_random_proxy()
            r = requests.get(
                "https://discord.com/api/v9/users/@me",
                headers={"Authorization": token.strip()},
                proxies=proxy,
                timeout=5
            )
            if r.status_code == 200:
                return r.json()
        except:
            continue
    return None

def sender_thread(task_id, token, channels, message, interval, jitter, auto_delete):
    channel_list = [c.strip() for c in channels.split(',') if c.strip()]
    while tasks.get(task_id, False):
        for ch_id in channel_list:
            if not tasks.get(task_id): break
            
            url = f"https://discord.com/api/v9/channels/{ch_id}/messages"
            headers = {"Authorization": token.strip(), "Content-Type": "application/json"}
            
            try:
                # [span_7](start_span)Her mesajda farklı proxy kullanarak ban riskini minimize ederiz[span_7](end_span)
                proxy = get_random_proxy()
                r = requests.post(url, json={"content": message}, headers=headers, proxies=proxy, timeout=7)
                
                if r.status_code == 200 and auto_delete:
                    msg_id = r.json().get('id')
                    time.sleep(1.5)
                    requests.delete(f"{url}/{msg_id}", headers=headers, proxies=proxy)
            except:
                pass

        wait = float(interval)
        if jitter: wait += random.uniform(0.1, 1.5)
        time.sleep(max(0.5, wait))

# Flask Route'ları (Giriş, Dashboard, API) buraya eklenecek...
# (Önceki kodlardaki @app.route kısımlarını aynen kullanabilirsin)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
