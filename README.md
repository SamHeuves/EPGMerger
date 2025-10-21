# 📺 EPG Merger

A simple yet powerful Python application for merging multiple Electronic Program Guide (EPG) XML files into unified feeds for IPTV applications. Built with Flask and designed for Docker deployment on Proxmox.

## ✨ Features

- 🔗 **Multiple EPG Files**: Create separate merged EPGs with different source combinations
- 🌐 **Web Interface**: Beautiful, modern UI with real-time feedback
- ⏰ **Auto-Scheduling**: Automatic updates every 2 hours (configurable)
- 📦 **Gzip Support**: Handles both plain XML and `.xml.gz` files
- 📊 **Statistics**: Real-time channel and programme counts
- 🐳 **Docker Ready**: Production-ready containerization
- 🔄 **Source Management**: Easy add/remove/test EPG sources
- 📡 **IPTV Integration**: Direct EPG URLs for any IPTV player

## 🚀 Quick Start

### Deploy to Proxmox from GitHub

1. **SSH into your Proxmox container:**

   ```bash
   ssh root@YOUR_PROXMOX_IP
   ```

2. **Clone and deploy:**

   ```bash
   cd /opt
   git clone https://github.com/YOUR_USERNAME/EPGMerger.git
   cd EPGMerger
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **Access your application:**
   ```
   http://YOUR_PROXMOX_IP:5000
   ```

That's it! The deployment script handles everything automatically.

## 📖 Documentation

- **[Deployment Guide](DEPLOYMENT.md)** - Complete GitHub to Proxmox deployment
- **[Docker Documentation](DOCKER.md)** - Docker setup and configuration
- **[Docker Testing](DOCKER_TEST.md)** - Local testing on Windows

## 🎯 Use Cases

- Combine EPG data from multiple sources
- Create region-specific EPG feeds
- Merge country-specific TV guides
- Provide unified EPG for IPTV services
- Automate EPG updates for set-top boxes

## 🌐 How It Works

1. **Add Sources**: Enter EPG XML URLs (supports `.xml` and `.xml.gz`)
2. **Create EPG Files**: Make multiple merged EPGs with different source combinations
3. **Get URLs**: Copy EPG download URLs for your IPTV player
4. **Auto-Update**: Application automatically refreshes every 2 hours

## 📡 IPTV Integration

Use the generated EPG URLs in your IPTV player:

```
http://YOUR_SERVER_IP:5000/api/epg-files/[EPG_ID]/download
```

### Compatible IPTV Players:

- TiviMate
- IPTV Smarters
- Perfect Player
- Kodi
- VLC
- Any XMLTV-compatible player

## 🛠️ Technical Stack

- **Backend**: Python 3.11, Flask
- **Scheduling**: APScheduler
- **XML Processing**: ElementTree
- **Frontend**: HTML5, CSS3, JavaScript
- **Container**: Docker, Docker Compose
- **Server**: Gunicorn (production)

## 📊 Features in Detail

### Multiple EPG Files

Create separate merged EPGs for different purposes:

- Regional EPG (NL channels only)
- Complete EPG (all sources)
- Custom combinations

### Source Management

- Add unlimited EPG sources
- Test sources before merging
- Enable/disable sources without deletion
- View statistics per source

### Auto-Scheduling

- Configurable merge intervals (default: 2 hours)
- Always fetches fresh data
- Runs in background
- Automatic failure recovery

### Statistics Dashboard

- Total channels per EPG
- Total programmes per EPG
- File sizes
- Last update timestamps
- Per-source statistics

## 🔧 Configuration

### Environment Variables

```bash
FLASK_ENV=production  # or development
TZ=UTC               # Your timezone
PORT=5000            # Custom port
```

### Data Persistence

- **Development**: `./data` directory
- **Production**: `epg_data` Docker volume

## 🔄 Updating

To update to the latest version:

```bash
cd /opt/EPGMerger
./deploy.sh
```

Or manually:

```bash
git pull origin main
docker-compose -f docker-compose.prod.yml up --build -d
```

## 📋 Requirements

### For Proxmox:

- Debian/Ubuntu container or VM
- Docker (auto-installed)
- 512MB RAM minimum
- 1GB disk space

### For Local Development:

- Python 3.11+
- Docker Desktop (optional)
- Git

## 🔒 Security Features

- Non-root container user
- Minimal base image (Alpine Linux)
- Health checks
- Resource limits
- Proper file permissions

## 📁 Project Structure

```
EPGMerger/
├── app.py                    # Main Flask application
├── templates/
│   └── index.html           # Web interface
├── data/
│   ├── config.json          # Application config
│   └── epg_files/           # Merged EPG files
├── Dockerfile               # Development image
├── Dockerfile.prod          # Production image
├── docker-compose*.yml      # Docker Compose configs
├── deploy.sh               # Deployment script
└── requirements.txt        # Python dependencies
```

## 🐛 Troubleshooting

### Container won't start

```bash
docker-compose -f docker-compose.prod.yml logs
```

### Can't access from network

```bash
# Check firewall
ufw status
ufw allow 5000/tcp
```

### Out of memory

Increase memory limit in `docker-compose.prod.yml`

See [DEPLOYMENT.md](DEPLOYMENT.md) for more troubleshooting.

## 📈 Performance

- Handles 50,000+ programmes efficiently
- Merges multiple large XML files in seconds
- Low resource usage (~100MB RAM)
- Supports concurrent requests

## 🎯 Roadmap

- [ ] API authentication
- [ ] EPG filtering by channel
- [ ] Custom merge schedules per EPG
- [ ] Webhook notifications
- [ ] Web-based configuration editor

## 📄 License

MIT License - feel free to use in personal and commercial projects.

## 🙏 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues, questions, or feature requests:

1. Check the [documentation](DEPLOYMENT.md)
2. Review [troubleshooting guide](DEPLOYMENT.md#-troubleshooting)
3. Open an issue on GitHub

## 🎉 Credits

Built with ❤️ for the IPTV community.

---

**Ready to get started?** Follow the [Deployment Guide](DEPLOYMENT.md) to deploy on Proxmox in minutes! 🚀
