#!/usr/bin/env python3
"""
Network Diagnostic Web Dashboard - NO AI VERSION
เหมือนเดิมแต่ไม่ต้องใช้ Anthropic API
ประหยัด cost และเร็วขึ้น!
"""

from flask import Flask, render_template_string, jsonify
import subprocess
import json
import re
import socket
import time
from datetime import datetime
import os

app = Flask(__name__)

# Store diagnostic results
diagnostic_results = {}
is_running = False

# ===== HTML Template (ไม่มี AI section) =====
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌐 Network Diagnostic Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
            animation: slideDown 0.5s ease-out;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.95;
        }
        
        .control-panel {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }
        
        .control-panel button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.1em;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .control-panel button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        
        .control-panel button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        .status-indicator.running {
            background: #4CAF50;
        }
        
        .status-indicator.idle {
            background: #9E9E9E;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .status-text {
            font-weight: bold;
            color: #333;
            margin-top: 10px;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border-left: 5px solid #667eea;
            transition: all 0.3s;
            animation: slideUp 0.5s ease-out;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        }
        
        .card.warning {
            border-left-color: #ff9800;
            background: #fff8f0;
        }
        
        .card.error {
            border-left-color: #f44336;
            background: #ffebee;
        }
        
        .card.success {
            border-left-color: #4CAF50;
            background: #f1f8f4;
        }
        
        .card h3 {
            margin-bottom: 15px;
            color: #333;
            font-size: 1.3em;
        }
        
        .card-item {
            margin: 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #eee;
            padding: 10px 0;
        }
        
        .card-item:last-child {
            border-bottom: none;
        }
        
        .card-label {
            font-weight: 600;
            color: #666;
        }
        
        .card-value {
            color: #333;
            font-size: 1.1em;
            font-weight: 500;
        }
        
        .badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            margin: 5px 0;
        }
        
        .badge.ok {
            background: #c8e6c9;
            color: #2e7d32;
        }
        
        .badge.warning {
            background: #ffe0b2;
            color: #e65100;
        }
        
        .badge.error {
            background: #ffcdd2;
            color: #c62828;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            display: none;
        }
        
        .spinner {
            border: 5px solid #f3f3f3;
            border-top: 5px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loading-text {
            color: white;
            font-size: 1.2em;
            font-weight: bold;
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .info-box {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            border-left: 5px solid #2196F3;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }

        .info-box h3 {
            color: #2196F3;
            margin-bottom: 10px;
        }

        .info-box p {
            color: #666;
            line-height: 1.6;
        }
        
        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 1.8em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 Network Diagnostic Dashboard</h1>
            <p>ตรวจสอบสภาพ WiFi และเครือข่าย</p>
        </div>
        
        <div class="control-panel">
            <button id="runBtn" onclick="runDiagnostic()">
                ▶️ เริ่มการตรวจสอบ
            </button>
            <div class="status-text">
                <span class="status-indicator idle" id="statusIndicator"></span>
                <span id="statusText">พร้อมสำหรับการตรวจสอบ</span>
            </div>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <div class="loading-text">🔍 กำลังตรวจสอบเครือข่าย...</div>
            <div class="loading-text" style="font-size: 0.9em; margin-top: 10px;">อาจใช้เวลาประมาณ 10-30 วินาที</div>
        </div>
        
        <div id="results"></div>
    </div>
    
    <script>
        let isRunning = false;
        
        async function runDiagnostic() {
            if (isRunning) return;
            
            isRunning = true;
            document.getElementById('runBtn').disabled = true;
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').innerHTML = '';
            document.getElementById('statusIndicator').className = 'status-indicator running';
            document.getElementById('statusText').textContent = 'กำลังตรวจสอบเครือข่าย...';
            
            try {
                const response = await fetch('/api/diagnostic', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                
                const data = await response.json();
                
                document.getElementById('loading').style.display = 'none';
                displayResults(data);
                
                document.getElementById('statusIndicator').className = 'status-indicator idle';
                document.getElementById('statusText').textContent = '✅ ตรวจสอบเสร็จแล้ว';
                
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('results').innerHTML = `
                    <div class="card error">
                        <h3>❌ เกิดข้อผิดพลาด</h3>
                        <p>${error.message}</p>
                    </div>
                `;
                document.getElementById('statusIndicator').className = 'status-indicator idle';
                document.getElementById('statusText').textContent = '❌ เกิดข้อผิดพลาด';
            } finally {
                isRunning = false;
                document.getElementById('runBtn').disabled = false;
            }
        }
        
        function displayResults(data) {
            let html = '';
            
            // System Info
            html += `
                <div class="dashboard">
                    <div class="card">
                        <h3>📱 ข้อมูลระบบ</h3>
                        <div class="card-item">
                            <span class="card-label">เซิร์ฟเวอร์:</span>
                            <span class="card-value">${data.system.server_info || 'Cloud'}</span>
                        </div>
                        <div class="card-item">
                            <span class="card-label">เวลา:</span>
                            <span class="card-value">${data.system.timestamp}</span>
                        </div>
                    </div>
            `;
            
            // WiFi Status
            const wifiCard = data.wifi.ssid ? 'success' : 'warning';
            html += `
                    <div class="card ${wifiCard}">
                        <h3>📶 WiFi Status</h3>
                        ${data.wifi.ssid ? `
                            <div class="card-item">
                                <span class="card-label">SSID:</span>
                                <span class="card-value">${data.wifi.ssid}</span>
                            </div>
                            <div class="card-item">
                                <span class="card-label">Signal:</span>
                                <span class="card-value">${data.wifi.signal_strength}%</span>
                            </div>
                            <div class="card-item">
                                <span class="card-label">Quality:</span>
                                <span class="card-value">
                                    <span class="badge ${getQualityClass(data.wifi.signal_quality)}">
                                        ${data.wifi.signal_quality}
                                    </span>
                                </span>
                            </div>
                        ` : `
                            <p>❌ ไม่มี WiFi connection</p>
                        `}
                    </div>
            `;
            
            // Network Performance
            const perfCard = data.performance.ping_avg && data.performance.ping_avg < 100 ? 'success' : 'warning';
            html += `
                    <div class="card ${perfCard}">
                        <h3>📊 Network Performance</h3>
                        ${data.performance.ping_avg ? `
                            <div class="card-item">
                                <span class="card-label">Ping (avg):</span>
                                <span class="card-value">${Math.round(data.performance.ping_avg)} ms</span>
                            </div>
                            <div class="card-item">
                                <span class="card-label">Status:</span>
                                <span class="card-value">
                                    <span class="badge ${data.performance.ping_status === 'Normal ✅' ? 'ok' : 'warning'}">
                                        ${data.performance.ping_status}
                                    </span>
                                </span>
                            </div>
                        ` : `
                            <p>⚠️ ไม่สามารถทดสอบได้</p>
                        `}
                    </div>
                </div>
            `;
            
            // DNS Performance
            html += `
                <div class="dashboard">
                    <div class="card ${data.dns.dns_status === 'Normal ✅' ? 'success' : 'warning'}">
                        <h3>🔎 DNS Performance</h3>
                        ${data.dns.google_resolution_ms ? `
                            <div class="card-item">
                                <span class="card-label">Google.com Resolution:</span>
                                <span class="card-value">${Math.round(data.dns.google_resolution_ms)} ms</span>
                            </div>
                            <div class="card-item">
                                <span class="card-label">Status:</span>
                                <span class="card-value">
                                    <span class="badge ${data.dns.dns_status === 'Normal ✅' ? 'ok' : 'warning'}">
                                        ${data.dns.dns_status}
                                    </span>
                                </span>
                            </div>
                        ` : `
                            <p>⚠️ DNS test failed</p>
                        `}
                    </div>
                    
                    <div class="card">
                        <h3>🔗 Network Status</h3>
                        ${data.connections ? `
                            <div class="card-item">
                                <span class="card-label">Established Connections:</span>
                                <span class="card-value">${data.connections.established_count || 0}</span>
                            </div>
                            <div class="card-item">
                                <span class="card-label">Listening Ports:</span>
                                <span class="card-value">${data.connections.listening_count || 0}</span>
                            </div>
                        ` : `
                            <p>Network data unavailable</p>
                        `}
                    </div>
            `;
            
            // Processes
            if (data.processes.bandwidth_consuming_apps && data.processes.bandwidth_consuming_apps.length > 0) {
                html += `
                    <div class="card warning">
                        <h3>⚙️ Bandwidth-Consuming Apps</h3>
                        <p>⚠️ พบแอปพลิเคชันต่อไปนี้:</p>
                        ${data.processes.bandwidth_consuming_apps.map(app => `
                            <div class="badge warning">${app}</div>
                        `).join('')}
                    </div>
                `;
            }
            
            html += `</div>`;

            // Information Box
            html += `
                <div class="info-box">
                    <h3>💡 Manual Analysis Required</h3>
                    <p>
                        AI analysis is currently disabled to save on API costs. 
                        Review the data above and check the following:
                    </p>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li><strong>WiFi Signal:</strong> If below 40%, consider moving closer to router or upgrading equipment</li>
                        <li><strong>Ping Time:</strong> If above 100ms, connection is slow. Check internet provider or network congestion</li>
                        <li><strong>Bandwidth Apps:</strong> If CCTV/ffmpeg detected, reduce resolution or frame rate</li>
                        <li><strong>DNS:</strong> If above 500ms, try changing DNS servers (8.8.8.8 or 1.1.1.1)</li>
                    </ul>
                </div>
            `;
            
            document.getElementById('results').innerHTML = html;
        }
        
        function getQualityClass(quality) {
            if (quality === 'Excellent') return 'ok';
            if (quality === 'Good') return 'ok';
            if (quality === 'Fair') return 'warning';
            return 'error';
        }
    </script>
</body>
</html>
"""

# ===== Routes =====
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/diagnostic', methods=['POST'])
def api_diagnostic():
    global is_running
    
    if is_running:
        return jsonify({"error": "Diagnostic already running"}), 400
    
    is_running = True
    try:
        results = {
            "system": get_system_info(),
            "wifi": get_wifi_signal(),
            "performance": get_network_performance(),
            "processes": get_high_bandwidth_processes(),
            "dns": get_dns_performance(),
            "connections": get_network_connections(),
        }
        
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        is_running = False

# ===== Diagnostic Functions (เหมือนเดิม) =====
def get_system_info():
    info = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "server_info": "Render.com Cloud"
    }
    return info

def get_wifi_signal():
    wifi = {"status": "unknown"}
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"] if os.name == 'nt' else ["iwconfig"],
            capture_output=True, text=True, timeout=5
        )
        
        for line in result.stdout.split('\n'):
            if 'SSID' in line or 'ssid' in line:
                if ':' in line:
                    wifi['ssid'] = line.split(':', 1)[1].strip()
            if 'Signal' in line or 'signal' in line:
                match = re.search(r'(\d+)%', line)
                if match:
                    signal = int(match.group(1))
                    wifi['signal_strength'] = signal
                    wifi['signal_quality'] = get_signal_quality(signal)
    except:
        pass
    
    return wifi

def get_network_performance():
    perf = {}
    try:
        result = subprocess.run(
            ["ping", "-n", "4", "8.8.8.8"] if os.name == 'nt' else ["ping", "-c", "4", "8.8.8.8"],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'min' in line or 'avg' in line:
                    match = re.search(r'(?:min|avg)[/=\s]+(\d+\.?\d*)', line, re.IGNORECASE)
                    if match:
                        perf['ping_avg'] = float(match.group(1))
            
            if perf.get('ping_avg'):
                perf['ping_status'] = "Normal ✅" if perf['ping_avg'] < 100 else "High ⚠️"
    except:
        pass
    
    return perf

def get_high_bandwidth_processes():
    processes = {"bandwidth_consuming_apps": []}
    try:
        result = subprocess.run(
            ["tasklist"] if os.name == 'nt' else ["ps", "aux"],
            capture_output=True, text=True, timeout=5
        )
        
        bandwidth_apps = ["motion", "ffmpeg", "vlc", "python", "java", "chrome"]
        for app in bandwidth_apps:
            if app.lower() in result.stdout.lower():
                processes["bandwidth_consuming_apps"].append(app)
    except:
        pass
    
    return processes

def get_dns_performance():
    dns = {}
    try:
        start = time.time()
        socket.gethostbyname("google.com")
        dns['google_resolution_ms'] = (time.time() - start) * 1000
        dns['dns_status'] = "Normal ✅" if dns['google_resolution_ms'] < 500 else "Slow ⚠️"
    except:
        dns['error'] = "DNS resolution failed"
    
    return dns

def get_network_connections():
    connections = {"established_count": 0, "listening_count": 0}
    try:
        result = subprocess.run(
            ["netstat", "-an"],
            capture_output=True, text=True, timeout=5
        )
        connections['established_count'] = len([l for l in result.stdout.split('\n') if 'ESTABLISHED' in l])
        connections['listening_count'] = len([l for l in result.stdout.split('\n') if 'LISTENING' in l])
    except:
        pass
    
    return connections

def get_signal_quality(signal_strength):
    if signal_strength >= 80:
        return "Excellent"
    elif signal_strength >= 60:
        return "Good"
    elif signal_strength >= 40:
        return "Fair"
    else:
        return "Poor"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
