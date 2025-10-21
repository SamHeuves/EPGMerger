# EPG Merger Docker Setup

## 🐳 Docker Files Created

### Core Files:

- **`Dockerfile`** - Development Docker image
- **`Dockerfile.prod`** - Production Docker image with Gunicorn
- **`docker-compose.yml`** - Standard Docker Compose
- **`docker-compose.dev.yml`** - Development with live reload
- **`docker-compose.prod.yml`** - Production with resource limits
- **`docker-entrypoint.sh`** - Entrypoint script for initialization

## 🚀 Quick Start Commands

### Development (with live reload):

```bash
docker-compose -f docker-compose.dev.yml up --build
```

### Production:

```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

### Standard:

```bash
docker-compose up --build -d
```

## 📋 Features

### Security:

- ✅ Non-root user (`epguser`)
- ✅ Proper file permissions
- ✅ Minimal base image

### Production Ready:

- ✅ Gunicorn WSGI server
- ✅ Health checks
- ✅ Resource limits
- ✅ Proper logging

### Development:

- ✅ Live code reload
- ✅ Volume mounting for instant changes
- ✅ Debug mode enabled

## 🔧 Configuration

### Environment Variables:

- `FLASK_ENV` - Set to `production` or `development`
- `TZ` - Timezone (default: UTC)
- `PORT` - Custom port (default: 5000)

### Volumes:

- `epg_data` - Persistent data storage
- `./data` - Development data mounting

## 📊 Health Checks

The container includes health checks that verify:

- Application is responding
- API endpoints are working
- Container is healthy

## 🌐 Access

Once running, access the application at:

- **Local**: http://localhost:5000
- **Network**: http://YOUR_SERVER_IP:5000

## 🔄 Auto-Update

The application will automatically:

- Merge EPG files every 2 hours (configurable)
- Restart on failure
- Maintain data persistence

## 📁 Data Persistence

All EPG files and configuration are stored in Docker volumes:

- **Development**: `./data` directory
- **Production**: `epg_data` Docker volume
