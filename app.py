#!/usr/bin/env python3
import os
import time
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# ตั้งค่า API Token
API_TOKEN = os.environ.get("AGENT_TOKEN", "mywifi-2026-xyz")

# เก็บข้อมูลรายงานล่าสุด
reports = {}

def signal_quality(signal):
    if signal is None: return "Unknown"
    if signal >= 80: return "Excellent"
    if signal >= 60: return "Good"
    if signal >= 40: return "Fair"
    return "Poor"

# ===================== API: รับข้อมูล =====================
@app.route('/api/report', methods=['POST'])
def api_report():
    data = request.get_json(silent=True) or {}
    if data.get("token") != API_TOKEN:
        return jsonify({"error": "unauthorized"}), 401

    computer = (data.get("computer") or "unknown").strip()
    reports[computer] = {
        "computer": computer,
        "ssid": data.get("ssid"),
        "bssid": data.get("bssid"),
        "signal": data.get("signal"),
        "signal_quality": signal_quality(data.get("signal")),
        "radio": data.get("radio"),
        "channel": data.get("channel"),
        "rx_rate": data.get("rx_rate"),
        "tx_rate": data.get("tx_rate"),
        "ping_avg": data.get("ping_avg"),
        "timestamp": data.get("timestamp"),
        "last_seen": time.time(), # เก็บเวลาล่าสุดที่ได้รับข้อมูล
        "received": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return jsonify({"status": "ok"})

# ===================== API: ดึงข้อมูล =====================
@app.route('/api/data')
def api_data():
    current_time = time.time()
    items = []
    for r in reports.values():
        # ถ้าไม่ส่งข้อมูลมาเกิน 20 วินาที ถือว่าหลุดการเชื่อมต่อ (Offline)
        r["is_online"] = (current_time - r["last_seen"]) <= 20
        items.append(r)
    
    # เรียง Online ขึ้นก่อน และตามด้วยเวลาที่อัปเดต
    items = sorted(items, key=lambda x: (not x["is_online"], x["received"]), reverse=False)
    return jsonify(items)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# ============================ HTML & CSS (Modern UI) ============================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Network Diagnostic Dashboard</title>
<style>
  :root {
    --bg: #f8f9fa; --card-bg: #ffffff; --text-main: #2d3748; --text-muted: #718096;
    --border: #e2e8f0; --accent: #4299e1; --success: #48bb78; --warning: #ed8936; --danger: #f56565;
  }
  * { margin:0; padding:0; box-sizing:border-box; font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
  body { background: var(--bg); color: var(--text-main); padding: 2rem; line-height: 1.5; }
  
  .container { max-width: 1280px; margin: 0 auto; }
  .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; border-bottom: 1px solid var(--border); padding-bottom: 1.5rem; }
  .header h1 { font-size: 1.5rem; font-weight: 600; color: var(--text-main); }
  .status-badge { display: inline-flex; align-items: center; background: white; padding: 0.5rem 1rem; border-radius: 9999px; border: 1px solid var(--border); font-size: 0.875rem; color: var(--text-muted); }
  .dot { width: 8px; height: 8px; border-radius: 50%; margin-right: 8px; }
  .dot.pulse { background: var(--success); box-shadow: 0 0 0 0 rgba(72, 187, 120, 0.7); animation: pulse 2s infinite; }
  
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 1.5rem; }
  
  .card { 
    background: var(--card-bg); border-radius: 12px; padding: 1.5rem; 
    border: 1px solid var(--border); transition: all 0.2s; position: relative; overflow: hidden;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  }
  .card.offline { border-color: var(--danger); opacity: 0.7; }
  .card.offline .status-dot { background: var(--danger); }
  .card.online .status-dot { background: var(--success); }
  
  .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.2rem; }
  .card-title { font-size: 1.125rem; font-weight: 600; display: flex; align-items: center; gap: 8px; }
  .status-dot { width: 10px; height: 10px; border-radius: 50%; }
  
  .data-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
  .data-item { display: flex; flex-direction: column; gap: 0.2rem; }
  .label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); font-weight: 600; }
  .value { font-size: 0.95rem; font-weight: 500; color: var(--text-main); }
  
  .badge { display: inline-block; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
  .bg-success { background: #f0fff4; color: #22543d; }
  .bg-warning { background: #fffaf0; color: #7b341e; }
  .bg-danger { background: #fff5f5; color: #742a2a; }
  
  .footer-data { margin-top: 1.2rem; padding-top: 1rem; border-top: 1px dashed var(--border); display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--text-muted); }
  
  .empty-state { text-align: center; padding: 4rem; color: var(--text-muted); background: white; border-radius: 12px; border: 1px dashed var(--border); }
  
  @keyframes pulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(72, 187, 120, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(72, 187, 120, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(72, 187, 120, 0); }
  }
</style>
</head>
<body>

<div class="container">
  <div class="header">
    <h1>🌐 Network Dashboard</h1>
    <div class="status-badge">
      <span class="dot pulse"></span>
      <span id="counter">กำลังซิงค์ข้อมูล...</span>
    </div>
  </div>

  <div id="results" class="grid"></div>
</div>

<script>
function getQualityBadge(q) {
  if (q === 'Excellent' || q === 'Good') return 'bg-success';
  if (q === 'Fair') return 'bg-warning';
  return 'bg-danger';
}

async function fetchData() {
  try {
    const res = await fetch('/api/data');
    const data = await res.json();
    const counter = document.getElementById('counter');
    const container = document.getElementById('results');

    if (!data.length) {
      counter.textContent = 'ยังไม่มีอุปกรณ์เชื่อมต่อ';
      container.innerHTML = `<div class="empty-state" style="grid-column: 1/-1;">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin: 0 auto 1rem; opacity: 0.5;">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
        </svg>
        <p>กำลังรออุปกรณ์ส่งข้อมูล...<br>กรุณารันไฟล์ agent.ps1 บนเครื่องเป้าหมาย</p>
      </div>`;
      return;
    }

    const onlineCount = data.filter(d => d.is_online).length;
    counter.textContent = `เชื่อมต่ออยู่ ${onlineCount} เครื่อง (จากทั้งหมด ${data.length})`;
    
    let html = '';
    for (const d of data) {
      const statusClass = d.is_online ? 'online' : 'offline';
      const statusText = d.is_online ? 'Online' : 'Offline';
      const sig = (d.signal != null) ? \`\${d.signal}%\` : '-';
      const ping = (d.ping_avg != null) ? \`\${d.ping_avg} ms\` : '-';
      const speed = (d.rx_rate || d.tx_rate) ? \`\${d.rx_rate || '-'} / \${d.tx_rate || '-'} Mbps\` : 'N/A';
      const channelInfo = d.channel ? \`Ch \${d.channel}\` : 'N/A';
      
      html += `
        <div class="card \${statusClass}">
          <div class="card-header">
            <div class="card-title">
              <div class="status-dot"></div>
              \${d.computer}
            </div>
            <span class="badge \${d.is_online ? 'bg-success' : 'bg-danger'}">\${statusText}</span>
          </div>
          
          <div class="data-grid">
            <div class="data-item">
              <span class="label">WiFi SSID</span>
              <span class="value">\${d.ssid || '-'}</span>
            </div>
            <div class="data-item">
              <span class="label">Signal Quality</span>
              <span class="value">
                \${sig} <span class="badge \${getQualityBadge(d.signal_quality)}" style="margin-left:4px">\${d.signal_quality}</span>
              </span>
            </div>
            <div class="data-item">
              <span class="label">Ping (8.8.8.8)</span>
              <span class="value">\${ping}</span>
            </div>
            <div class="data-item">
              <span class="label">Rx / Tx Speed</span>
              <span class="value">\${speed}</span>
            </div>
            <div class="data-item">
              <span class="label">Radio / Channel</span>
              <span class="value">\${d.radio || '-'} | \${channelInfo}</span>
            </div>
            <div class="data-item">
              <span class="label">BSSID (MAC Address)</span>
              <span class="value" style="font-size: 0.8rem; font-family: monospace;">\${d.bssid || '-'}</span>
            </div>
          </div>
          
          <div class="footer-data">
            <span>อัปเดตล่าสุด: \${d.is_online ? 'เมื่อสักครู่' : d.received}</span>
          </div>
        </div>`;
    }
    container.innerHTML = html;
  } catch (e) {
    document.getElementById('counter').textContent = 'ขาดการเชื่อมต่อกับเซิร์ฟเวอร์';
  }
}

fetchData();
setInterval(fetchData, 5000); // รีเฟรชหน้าเว็บทุกๆ 5 วินาทีเพื่อให้ดู Real-time มากขึ้น
</script>
</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
