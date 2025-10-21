# 🐙 GitHub Setup Guide

Complete guide to push your EPG Merger to GitHub and deploy to Proxmox.

---

## 📋 Step-by-Step GitHub Setup

### 1. Create GitHub Repository

1. Go to https://github.com
2. Click **"New repository"** or go to https://github.com/new
3. Fill in:
   - **Repository name**: `EPGMerger`
   - **Description**: `EPG XML Merger for IPTV - Combines multiple EPG sources`
   - **Visibility**: Public or Private (your choice)
   - **DO NOT** initialize with README (we have one)
4. Click **"Create repository"**

---

### 2. Push Your Code to GitHub

Open PowerShell in your `EPGMerger` folder and run:

```powershell
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - EPG Merger application"

# Add your GitHub repository as remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/EPGMerger.git

# Push to GitHub
git push -u origin main
```

If you get an error about "master" vs "main", run:

```powershell
git branch -M main
git push -u origin main
```

---

### 3. Configure Git (First Time Only)

If git asks for credentials:

```powershell
# Set your name
git config --global user.name "Your Name"

# Set your email
git config --global user.email "your.email@example.com"
```

For authentication, you have two options:

#### Option A: Personal Access Token (Recommended)

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` permissions
3. Use the token as your password when pushing

#### Option B: SSH Key

1. Generate SSH key:
   ```powershell
   ssh-keygen -t ed25519 -C "your.email@example.com"
   ```
2. Add to GitHub: Settings → SSH and GPG keys → New SSH key
3. Change remote URL:
   ```powershell
   git remote set-url origin git@github.com:YOUR_USERNAME/EPGMerger.git
   ```

---

## 🚀 Deploy to Proxmox

Once your code is on GitHub:

### Quick Deploy Method

1. **SSH into Proxmox:**

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

3. **Access your app:**
   ```
   http://YOUR_PROXMOX_IP:5000
   ```

### The deploy script will:

- ✅ Install Docker if needed
- ✅ Install Docker Compose if needed
- ✅ Build the application
- ✅ Start containers in production mode
- ✅ Show access URLs

---

## 🔄 Update Workflow

### On Windows (Development):

1. Make changes to your code
2. Test locally:
   ```powershell
   python app.py
   ```
3. Commit and push:
   ```powershell
   git add .
   git commit -m "Description of changes"
   git push origin main
   ```

### On Proxmox (Production):

1. SSH into Proxmox:

   ```bash
   ssh root@YOUR_PROXMOX_IP
   ```

2. Update and redeploy:
   ```bash
   cd /opt/EPGMerger
   ./deploy.sh
   ```

That's it! The script pulls latest changes and rebuilds automatically.

---

## 📁 What Gets Pushed to GitHub

✅ **Included:**

- Source code (`app.py`, `templates/`)
- Docker configuration files
- Documentation
- Requirements
- Deployment scripts
- Directory structure

❌ **Excluded** (via `.gitignore`):

- `data/config.json` (user config)
- `data/epg_files/*.xml` (generated EPG files)
- Python cache files
- Virtual environments
- IDE files

---

## 🔒 Security Best Practices

### Don't Commit:

- ❌ API keys or passwords
- ❌ Personal configuration
- ❌ Generated EPG files
- ❌ `.env` files with secrets

### Do Commit:

- ✅ Source code
- ✅ Docker configurations
- ✅ Documentation
- ✅ Example configurations

The `.gitignore` is already set up to protect sensitive files!

---

## 🌟 Repository Structure on GitHub

After pushing, your GitHub repo will look like:

```
EPGMerger/
├── .github/              (optional CI/CD)
├── .gitignore           (what to exclude)
├── .dockerignore        (Docker build exclusions)
├── app.py               (main application)
├── templates/
│   └── index.html
├── data/
│   ├── .gitkeep         (keeps folder in git)
│   └── epg_files/
│       └── .gitkeep
├── requirements.txt
├── Dockerfile
├── Dockerfile.prod
├── docker-compose.yml
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── docker-entrypoint.sh
├── deploy.sh
├── README.md
├── DEPLOYMENT.md
├── DOCKER.md
└── example_config.json
```

---

## 🎯 Complete Workflow Example

### Initial Setup:

```powershell
# On Windows
cd C:\Users\Admin\EPGMerger
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/EPGMerger.git
git push -u origin main
```

### Deploy to Proxmox:

```bash
# On Proxmox
cd /opt
git clone https://github.com/YOUR_USERNAME/EPGMerger.git
cd EPGMerger
chmod +x deploy.sh
./deploy.sh
```

### Make Updates:

```powershell
# On Windows - make changes, then:
git add .
git commit -m "Updated feature X"
git push origin main
```

```bash
# On Proxmox - deploy updates:
cd /opt/EPGMerger
./deploy.sh
```

---

## 🔧 Troubleshooting

### "Permission denied" when pushing

- Use Personal Access Token instead of password
- Or set up SSH key authentication

### "Remote origin already exists"

```powershell
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/EPGMerger.git
```

### Can't clone on Proxmox

```bash
# Install git first
apt-get update
apt-get install -y git
```

### Deploy script not executable

```bash
chmod +x deploy.sh
```

---

## 🎉 Success Checklist

After setup, you should have:

- [ ] Code pushed to GitHub
- [ ] Repository accessible at github.com/YOUR_USERNAME/EPGMerger
- [ ] Application deployed on Proxmox
- [ ] Web interface accessible at http://PROXMOX_IP:5000
- [ ] EPG URLs working in IPTV player
- [ ] Auto-merge running every 2 hours

---

## 📞 Next Steps

1. **Test locally** on Windows first
2. **Push to GitHub** using the commands above
3. **Deploy to Proxmox** using the deploy script
4. **Configure EPG sources** in the web interface
5. **Add EPG URLs** to your IPTV player
6. **Enjoy automated EPG updates!** 🎉

---

Ready to deploy? Follow the commands above and you'll be running in minutes! 🚀
