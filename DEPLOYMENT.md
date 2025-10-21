# 🚀 EPG Merger - GitHub to Proxmox Deployment Guide

Complete guide for deploying EPG Merger from GitHub to Proxmox.

---

## 📋 Prerequisites

### On Your Proxmox Container/VM:

- Debian/Ubuntu based container or VM
- Root or sudo access
- Internet connection
- Git installed
- Docker (will be installed if not present)

---

## 🎯 Deployment Options

### **Option 1: Quick Deploy (Recommended)**

Use this method for the easiest deployment:

#### 1. SSH into your Proxmox container

```bash
ssh root@YOUR_PROXMOX_IP
```

#### 2. Install Git (if not already installed)

```bash
apt-get update
apt-get install -y git
```

#### 3. Clone the repository

```bash
cd /opt
git clone https://github.com/YOUR_USERNAME/EPGMerger.git
cd EPGMerger
```

#### 4. Run the deployment script

```bash
chmod +x deploy.sh
./deploy.sh
```

That's it! The script will:

- ✅ Install Docker if needed
- ✅ Install Docker Compose if needed
- ✅ Build the application
- ✅ Start the containers
- ✅ Show you the access URLs

---

### **Option 2: Manual Deploy**

If you prefer manual control:

#### 1. SSH into Proxmox and clone

```bash
ssh root@YOUR_PROXMOX_IP
cd /opt
git clone https://github.com/YOUR_USERNAME/EPGMerger.git
cd EPGMerger
```

#### 2. Install Docker (if needed)

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh
```

#### 3. Install Docker Compose (if needed)

```bash
apt-get update
apt-get install -y docker-compose-plugin
```

#### 4. Deploy

```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

#### 5. Check status

```bash
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 🔄 Updating the Application

To update to the latest version from GitHub:

```bash
cd /opt/EPGMerger
./deploy.sh
```

Or manually:

```bash
cd /opt/EPGMerger
git pull origin main
docker-compose -f docker-compose.prod.yml up --build -d
```

---

## 🌐 Accessing Your Application

After deployment, access your EPG Merger at:

- **Web Interface**: http://YOUR_PROXMOX_IP:5000
- **EPG Downloads**: http://YOUR_PROXMOX_IP:5000/api/epg-files/[EPG_ID]/download

---

## 📊 Management Commands

### View logs

```bash
cd /opt/EPGMerger
docker-compose -f docker-compose.prod.yml logs -f
```

### Stop the application

```bash
docker-compose -f docker-compose.prod.yml down
```

### Restart the application

```bash
docker-compose -f docker-compose.prod.yml restart
```

### Check status

```bash
docker-compose -f docker-compose.prod.yml ps
```

### View resource usage

```bash
docker stats epg-merger
```

---

## 🔧 Configuration

### Change Port

Edit `docker-compose.prod.yml`:

```yaml
ports:
  - "8080:5000" # Change 8080 to your desired port
```

### Change Auto-Merge Interval

The application is configured for 2-hour intervals. To change:

1. Access the web interface
2. Update configuration in the UI, or
3. Edit `data/config.json` and restart

### Data Location

Application data is stored in:

- **Development**: `./data` directory
- **Production**: `epg_data` Docker volume

To backup data:

```bash
docker run --rm -v epg_data:/data -v $(pwd):/backup alpine tar czf /backup/epg-backup.tar.gz -C /data .
```

To restore data:

```bash
docker run --rm -v epg_data:/data -v $(pwd):/backup alpine tar xzf /backup/epg-backup.tar.gz -C /data
```

---

## 🔥 Firewall Configuration

If you have a firewall, allow port 5000:

### UFW (Ubuntu/Debian)

```bash
ufw allow 5000/tcp
ufw reload
```

### iptables

```bash
iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
```

---

## 🐛 Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Check Docker status
systemctl status docker

# Restart Docker
systemctl restart docker
```

### Port already in use

```bash
# Check what's using port 5000
netstat -tulpn | grep 5000

# Kill the process or change the port in docker-compose.prod.yml
```

### Can't access from network

```bash
# Check if container is running
docker ps

# Check if port is exposed
docker port epg-merger

# Check firewall rules
ufw status
```

### Out of memory errors

```bash
# Increase memory limits in docker-compose.prod.yml
mem_limit: 2g  # Change from 1g to 2g
```

---

## 📱 IPTV Setup

Once deployed, use these URLs in your IPTV player's EPG settings:

```
http://YOUR_PROXMOX_IP:5000/api/epg-files/[EPG_ID]/download
```

You can find the exact URLs in the web interface after creating your EPG files.

### Popular IPTV Players:

- **TiviMate**: Settings → EPG → Add EPG source
- **IPTV Smarters**: Settings → EPG → EPG URL
- **Perfect Player**: Settings → EPG → Remote XMLTV file

---

## 🎯 Post-Deployment Checklist

- [ ] Application accessible at http://YOUR_PROXMOX_IP:5000
- [ ] Add EPG source URLs
- [ ] Create merged EPG file(s)
- [ ] Test EPG download URLs
- [ ] Configure IPTV player with EPG URL
- [ ] Verify auto-merge is working (check logs after 2 hours)
- [ ] Set up backups (optional)
- [ ] Configure firewall rules (if needed)

---

## 📞 Support

If you encounter issues:

1. Check the logs: `docker-compose -f docker-compose.prod.yml logs`
2. Verify Docker is running: `systemctl status docker`
3. Check network connectivity: `curl http://localhost:5000`
4. Review this guide for common solutions

---

## 🎉 Success!

Your EPG Merger is now running on Proxmox and will:

- ✅ Auto-merge EPG files every 2 hours
- ✅ Handle gzipped XML files
- ✅ Provide stable EPG URLs for IPTV
- ✅ Restart automatically on failure
- ✅ Maintain data persistence

Enjoy your automated EPG management! 🚀
