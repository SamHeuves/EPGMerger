# EPG Merger - Docker Test Instructions

## 🐳 Docker Setup Complete!

Your EPG Merger application is now fully dockerized and ready for deployment.

## 📋 Quick Test (Windows)

### 1. Start Docker Desktop

Make sure Docker Desktop is running on your Windows machine.

### 2. Test Development Build

```bash
docker-compose -f docker-compose.dev.yml up --build
```

### 3. Test Production Build

```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

## 🚀 For Proxmox Deployment

### Option 1: Copy Files to Proxmox

1. Copy the entire `EPGMerger` folder to your Proxmox container/VM
2. SSH into the Proxmox container
3. Run: `docker-compose -f docker-compose.prod.yml up --build -d`

### Option 2: Build Image Locally, Push to Registry

1. Build the image: `docker build -f Dockerfile.prod -t epg-merger:latest .`
2. Tag for registry: `docker tag epg-merger:latest your-registry/epg-merger:latest`
3. Push: `docker push your-registry/epg-merger:latest`
4. Pull on Proxmox: `docker pull your-registry/epg-merger:latest`

## 📡 Access URLs

Once running, your EPG URLs will be:

- **Main Interface**: http://YOUR_SERVER_IP:5000
- **EPG Download**: http://YOUR_SERVER_IP:5000/api/epg-files/[EPG_ID]/download

## 🔧 Configuration

The application will:

- ✅ Auto-merge EPG files every 2 hours
- ✅ Store data persistently in Docker volumes
- ✅ Restart automatically on failure
- ✅ Handle gzipped XML files (.xml.gz)
- ✅ Support multiple EPG files with custom source combinations

## 📊 Features Included

- **Multiple EPG Files**: Create separate merged EPGs for different regions
- **Source Management**: Add/remove/test EPG source URLs
- **Auto-Scheduling**: Automatic updates every 2 hours
- **Web Interface**: Beautiful UI with loading states
- **IPTV Integration**: Direct EPG URLs for IPTV players
- **Statistics**: Real-time channel and programme counts

## 🛠️ Troubleshooting

### Docker Desktop Not Running

- Start Docker Desktop from Windows Start menu
- Wait for it to fully initialize (green icon in system tray)

### Permission Issues

- The entrypoint script permissions are handled automatically by Docker
- No manual `chmod` needed on Windows

### Port Conflicts

- Change the port in `docker-compose.yml` if 5000 is in use
- Update the `ports` section: `"8080:5000"` for port 8080

## 🎯 Next Steps

1. **Test locally** with Docker Desktop running
2. **Deploy to Proxmox** using one of the methods above
3. **Configure your IPTV** with the EPG URLs
4. **Set up monitoring** to ensure the service stays running

Your EPG Merger is ready for production! 🚀
