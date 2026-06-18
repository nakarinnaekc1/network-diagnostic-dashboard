# Network Diagnostic Dashboard

🌐 AI-Powered Network Diagnostic Tool deployed on Render.com

## Features

✨ **Web-Based Interface**
- Beautiful, responsive design
- Real-time diagnostics
- No installation required for clients

🤖 **AI-Powered Analysis**
- Claude Opus 4.6 integration
- Natural language insights
- Actionable recommendations in Thai

📊 **Comprehensive Diagnostics**
- WiFi signal strength analysis
- Network performance (ping test)
- DNS resolution speed
- Bandwidth-consuming applications detection
- Network connections statistics

## Supported Platforms

- ✅ Windows (primary)
- ✅ Linux
- ✅ macOS (partial - some system commands may vary)

## Quick Start

### Option 1: Local Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set API Key
export ANTHROPIC_API_KEY='sk-ant-your-key-here'

# Run application
python app.py

# Open browser
# http://localhost:5000
```

### Option 2: Render.com Deployment

See `RENDER_DEPLOY_GUIDE.txt` for detailed instructions.

1. Push to GitHub
2. Connect Render
3. Set `ANTHROPIC_API_KEY` environment variable
4. Deploy

## Installation

### Requirements
- Python 3.11+
- Flask
- Anthropic API key (from anthropic.com)

### Local Setup

```bash
git clone https://github.com/YOUR_USERNAME/network-diagnostic-dashboard.git
cd network-diagnostic-dashboard

pip install -r requirements.txt
export ANTHROPIC_API_KEY='sk-ant-your-key'

python app.py
```

## Configuration

### Environment Variables

```
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
PORT=5000  # Optional, defaults to 5000
```

### For Render.com

1. Go to Render Dashboard
2. Select Web Service
3. Environment tab
4. Add: `ANTHROPIC_API_KEY=sk-ant-xxx`

## Usage

1. Open web browser
2. Navigate to application URL
3. Click "▶️ เริ่มการตรวจสอบ" button
4. Wait 30-60 seconds for results
5. Review AI analysis and recommendations

## API Endpoints

### GET /
Main web interface

### POST /api/diagnostic
Run diagnostic test

**Response:**
```json
{
  "system": { ... },
  "wifi": { ... },
  "performance": { ... },
  "dns": { ... },
  "connections": { ... },
  "processes": { ... },
  "ai_analysis": "string"
}
```

## Architecture

- **Backend**: Flask (Python)
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript
- **AI**: Anthropic Claude Opus 4.6
- **Server**: Gunicorn (production)

## Diagnostics Included

### System Information
- Computer name
- Operating system
- Timestamp

### WiFi Status
- SSID
- Signal strength (%)
- Signal quality (Excellent/Good/Fair/Poor)

### Network Performance
- Ping to 8.8.8.8
- Min/Max/Average response time
- Status indicator

### DNS Performance
- Google.com resolution time
- DNS status

### Bandwidth Analysis
- Detects CCTV, ffmpeg, motion, etc.
- Shows high-bandwidth applications

### Network Connections
- Established connections count
- Listening ports count

### AI Recommendations
- Problem identification
- Root cause analysis
- Action steps (easy/intermediate/IT support)
- Next steps for investigation

## Performance

- **Diagnostic Time**: 30-60 seconds
- **API Response Time**: 15-40 seconds (AI analysis)
- **Cold Start (Free Tier)**: ~30 seconds
- **After Warmup**: 5-10 seconds

## Troubleshooting

### "API Key not configured"
```bash
export ANTHROPIC_API_KEY='sk-ant-your-key'
# or in Render: Set in Environment Variables
```

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "Address already in use"
- Change port in app.py: `port=5001`
- or kill process using port 5000

### Service not responding
- Check Render logs
- Verify API key is set
- Ensure internet connection

## Deployment

### Render.com (Recommended)

See `RENDER_DEPLOY_GUIDE.txt`

```bash
git push origin main
# Render auto-deploys
```

### Local Server

```bash
python app.py
```

### Docker (Optional)

```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
CMD ["gunicorn", "app:app"]
```

## Security Notes

⚠️ Free tier limitations on Render:
- Service sleeps after 15 minutes of inactivity
- First request takes ~30 seconds (cold start)
- Limited to free tier API usage

✅ Best practices:
- Keep API key secure
- Monitor Anthropic API usage
- Use HTTPS (Render provides)
- Don't share dashboard URL publicly

## Monitoring

### Render.com Dashboard
- View real-time logs
- Monitor build status
- Check resource usage

### Anthropic API Console
- Monitor API usage
- Check billing
- View rate limits

## Performance Tips

1. **For Local Deployment**
   - Run on same network as diagnostic targets
   - Use Ethernet for better results

2. **For Cloud Deployment**
   - Upgrade from Free tier if needed ($7/month)
   - Monitor cold start impact
   - Consider regional deployment

3. **Network Diagnostics**
   - Run multiple times to find patterns
   - Compare results over time
   - Check CCTV/streaming app settings

## Languages Supported

- ✅ Thai (ไทย)
- ✅ English (in code/logs)

## Future Enhancements

- [ ] Multi-language support
- [ ] Database for historical data
- [ ] Scheduled diagnostics
- [ ] Email notifications
- [ ] Advanced analytics dashboard
- [ ] Mobile app
- [ ] API authentication

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License

## Support

For issues and questions:
1. Check `RENDER_DEPLOY_GUIDE.txt`
2. Review Render logs
3. Test locally with `python app.py`

## Links

- [Render.com](https://render.com)
- [Flask Documentation](https://flask.palletsprojects.com)
- [Anthropic API](https://anthropic.com/api)

---

🚀 Deployed on Render.com Cloud Platform
🤖 Powered by Claude Opus 4.6
💜 Built with Flask & Python
