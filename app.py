#!/usr/bin/env python3
"""
Network Diagnostic Dashboard - Agent Edition
รันบน Render.com เป็นตัวรับข้อมูล + แสดงผล
ข้อมูล WiFi/Ping ถูกเก็บจากเครื่อง User ผ่าน agent.ps1 แล้วส่งมาที่ /api/report
"""

from flask import Flask, render_template_string, jsonify, request
from datetime import datetime
import os

app = Flask(__name__)

# token ต้องตรงกับที่ตั้งใน agent.ps1  (ตั้งค่าได้ที่ Render -> Environment)
API_TOKEN = os.environ.get("AGENT_TOKEN", "change-me-to-a-secret")

# เก็บรายงานล่าสุดของแต่ละเครื่องไว้ในหน่วยความจำ { computer_name: {...} }
reports = {}


def signal_quality(signal):
    if signal is None:
        return "Unknown"
    if signal >= 80:
        return "Excellent"
    if signal >= 60:
        return "Good"
    if signal >= 40:
        return "Fair"
    return "Poor"


# ===================== API: รับข้อมูลจาก Agent =====================
@app.route('/api/report', methods=['POST'])
def api_report():
    data = request.get_json(silent=True) or {}
    if data.get("token") != API_TOKEN:
        return jsonify({"error": "unauthorized"}), 401

    computer = (data.get("computer") or "unknown").strip()
    reports[computer] = {
        "computer": computer,
        "ssid": data.get("ssid"),
        "signal": data.get("signal"),
        "signal_quality": signal_quality(data.get("signal")),
        "ping_avg": data.get("ping_avg"),
        "timestamp": data.get("timestamp"),
        "received": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return jsonify({"status": "ok"})


# ===================== API: ให้ Dashboard ดึงไปแสดง =====================
@app.route('/api/data')
def api_data():
    # เรียงตามเครื่องที่ส่งมาล่าสุดก่อน
    items = sorted(reports.values(), key=lambda r: r["received"], reverse=True)
    return jsonify(items)


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


# ============================ HTML ============================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🌐 Network Diagnostic Dashboard</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family:'Segoe UI', Tahoma, sans-serif;
    background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
    min-height:100vh; padding:20px; color:#333;
  }
  .container { max-width:1200px; margin:0 auto; }
  .header { text-align:center; color:#fff; margin-bottom:24px; }
  .header h1 { font-size:2.3em; text-shadow:2px 2px 4px rgba(0,0,0,.3); }
  .header p { opacity:.95; margin-top:6px; }
  .bar {
    background:#fff; border-radius:14px; padding:16px 22px; margin-bottom:24px;
    display:flex; align-items:center; justify-content:space-between;
    box-shadow:0 10px 30px rgba(0,0,0,.18); flex-wrap:wrap; gap:10px;
  }
  .bar .status { font-weight:600; }
  .dot { display:inline-block; width:11px; height:11px; border-radius:50%;
         background:#4CAF50; margin-right:7px; }
  .dashboard { display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr));
               gap:20px; }
  .card {
    background:#fff; border-radius:15px; padding:22px;
    box-shadow:0 10px 30px rgba(0,0,0,.12); border-left:5px solid #667eea;
    transition:.25s;
  }
  .card:hover { transform:translateY(-4px); }
  .card.good { border-left-color:#4CAF50; background:#f1f8f4; }
  .card.fair { border-left-color:#ff9800; background:#fff8f0; }
  .card.poor { border-left-color:#f44336; background:#ffebee; }
  .card h3 { margin-bottom:14px; font-size:1.25em; }
  .row { display:flex; justify-content:space-between; padding:9px 0;
         border-bottom:1px solid #eee; }
  .row:last-child { border-bottom:none; }
  .label { color:#666; font-weight:600; }
  .badge { padding:4px 12px; border-radius:20px; font-size:.85em; font-weight:bold; }
  .badge.ok { background:#c8e6c9; color:#2e7d32; }
  .badge.warn { background:#ffe0b2; color:#e65100; }
  .badge.bad { background:#ffcdd2; color:#c62828; }
  .empty { background:#fff; border-radius:15px; padding:40px; text-align:center;
           color:#777; box-shadow:0 10px 30px rgba(0,0,0,.1); }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>🌐 Network Diagnostic Dashboard</h1>
    <p>ข้อมูลจากเครื่อง User ที่รัน Agent อยู่</p>
  </div>

  <div class="bar">
    <span class="status"><span class="dot"></span><span id="count">กำลังโหลด...</span></span>
    <span style="color:#888">รีเฟรชอัตโนมัติทุก 10 วินาที</span>
  </div>

  <div id="results"></div>
</div>

<script>
function qClass(q){
  if(q==='Excellent'||q==='Good') return 'good';
  if(q==='Fair') return 'fair';
  if(q==='Poor') return 'poor';
  return '';
}
function qBadge(q){
  if(q==='Excellent'||q==='Good') return 'ok';
  if(q==='Fair') return 'warn';
  if(q==='Poor') return 'bad';
  return 'warn';
}

async function load(){
  try{
    const res = await fetch('/api/data');
    const data = await res.json();
    const count = document.getElementById('count');
    const box = document.getElementById('results');

    if(!data.length){
      count.textContent = 'ยังไม่มีเครื่องส่งข้อมูลเข้ามา';
      box.innerHTML = '<div class="empty">⏳ รอ Agent ส่งข้อมูล...<br><br>'
        + 'เปิด run-agent.bat บนเครื่องที่ต้องการตรวจ แล้วรอสักครู่</div>';
      return;
    }

    count.textContent = data.length + ' เครื่องกำลังรายงาน';
    let html = '<div class="dashboard">';
    for(const d of data){
      const sig = (d.signal!=null) ? d.signal+'%' : 'ไม่มีสัญญาณ WiFi';
      const ping = (d.ping_avg!=null) ? d.ping_avg+' ms' : '-';
      const pingOk = (d.ping_avg!=null && d.ping_avg<100);
      html += `
        <div class="card ${qClass(d.signal_quality)}">
          <h3>💻 ${d.computer}</h3>
          <div class="row"><span class="label">WiFi (SSID):</span>
            <span>${d.ssid || '-'}</span></div>
          <div class="row"><span class="label">สัญญาณ:</span>
            <span>${sig}</span></div>
          <div class="row"><span class="label">คุณภาพ:</span>
            <span class="badge ${qBadge(d.signal_quality)}">${d.signal_quality}</span></div>
          <div class="row"><span class="label">Ping (8.8.8.8):</span>
            <span><span class="badge ${pingOk?'ok':'warn'}">${ping}</span></span></div>
          <div class="row"><span class="label">เวลาที่วัด:</span>
            <span>${d.timestamp || '-'}</span></div>
          <div class="row"><span class="label">รับเข้าระบบ:</span>
            <span>${d.received}</span></div>
        </div>`;
    }
    html += '</div>';
    box.innerHTML = html;
  }catch(e){
    document.getElementById('count').textContent = 'เชื่อมต่อ Dashboard ไม่ได้';
  }
}

load();
setInterval(load, 10000);
</script>
</body>
</html>
"""


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
