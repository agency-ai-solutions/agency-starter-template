# Agency Swarm GitHub App Deployment Template

Deploy your Agency Swarm agencies as production-ready GitHub Apps with automated Docker containerization and seamless integration.

<!-- **Video resource:** -->

---

## 🚀 Quick Start Guide

### Step 1: Use This Template to Create Your Repository

1. **Click the "Use this template" button** at the top of this repository
   - Or use this direct link: [Create new repository from template](https://github.com/agency-ai-solutions/agency-github-template/generate)

2. **Configure your new repository:**
   - Choose a repository name (e.g., `my-agency-deployment`)
   - Select your account or organization
   - Choose visibility (Public or Private)
   - Click **"Create repository from template"**

3. **Clone your new repository:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
   cd YOUR-REPO-NAME
   ```

### Step 2: Connect Agencii GitHub App to Your Repository

1. **Install the Agencii GitHub App:**
   - Go to your repository settings
   - Navigate to **"Integrations"** → **"GitHub Apps"**
   - Search for and install the **"Agencii"** GitHub App
   - Grant necessary permissions to your repository

### Step 3: Configure Your Agency and Deploy

1. **Set up environment variables:**
   - Copy `.env.example` to `.env` and add your API keys:
   ```bash
   cp src/.env.example src/.env
   ```
   - Add your OpenAI API key and other required variables

2. **Add your Agency Swarm agency:**
   - Replace the `ExampleAgency` folder in `/src` with your own agency
   - Ensure your agency follows the required structure:
   ```
   src/
   ├── YourAgency/
   │   ├── agency.py          # Must have create_agency() function
   │   ├── agency_manifesto.md
   │   ├── Agent1/
   │   │   ├── Agent1.py
   │   │   ├── instructions.md
   │   │   └── tools/
   │   └── Agent2/
   │       ├── Agent2.py
   │       ├── instructions.md
   │       └── tools/
   ```

3. **Update imports in main files:**
   - Edit `main.py` and `demo.py` to import your agency:
   ```python
   from YourAgency.agency import agency
   ```

4. **Configure deployment settings:**
   - Edit `src/agencii_config.json` to customize your deployment:
   ```json
   {
     "name": "Your Agency Name",
     "description": "Your agency description",
     "version": "1.0.0",
     "deployment_settings": {
       "memory_limit": "1024",
       "cpu_limit": "1",
       "lifecycle_timeout": 300
     }
   }
   ```

5. **Test locally (optional):**
   ```bash
   cd src
   python demo.py
   ```

6. **Deploy to production:**
   ```bash
   git add .
   git commit -m "Configure agency for deployment"
   git push origin main
   ```

The Agencii GitHub App will automatically detect your push and deploy your agency! 🎉

---

## 📋 Prerequisites

- A fully tested Agency Swarm agency
- GitHub account with repository access
- OpenAI API key
- Docker installed (optional for local testing)
- Python 3.12+ (for local testing)

## 🛠️ Advanced Configuration

### Custom Requirements
Add your extra Python packages to `src/requirements.txt`:
```txt
your-custom-package==1.0.0
another-package>=2.0.0
```

### Docker Configuration
Modify the `Dockerfile` for custom Docker setups:
- Change base image
- Add system dependencies
- Configure runtime environment

## 🔧 Troubleshooting

### Common Issues

**Agency not deploying:**
- Check that your `agency.py` has a `create_agency()` function
- Verify all required environment variables are set
- Ensure your agency structure matches the expected format

**Docker build failures:**
- Check `requirements.txt` for conflicting packages
- Verify all imports in your agency code
- Review Docker logs in Actions tab

**GitHub App connection issues:**
- Confirm App is installed on your repository
- Check repository permissions
- Verify webhook delivery in App settings

### Getting Help

- 📚 [Documentation](https://agency-swarm.ai/welcome/overview)
- 🐛 [Report Issues](https://github.com/agency-ai-solutions/agency-github-template/issues)

---

## 📖 What's Included

This template provides:
- 📦 **Docker Configuration**: Pre-configured containerization
- 🔧 **FastAPI Integration**: AG-UI protocol support
- ⚙️ **GitHub Actions**: Automated CI/CD workflows
- 📋 **Example Agency**: Complete reference implementation
- 🛠️ **Deployment Config**: Production-ready settings
- 🔒 **Security**: Secret scanning and protection

## 🎯 Key Features

- **🚀 One-Click Deployment**: From template to production in minutes
- **🔄 Auto-Scaling**: Configurable resource limits and lifecycle management
- **🛡️ Security First**: Built-in secret scanning and secure deployment
- **📊 Monitoring**: Integrated logging and performance tracking
- **🔧 Full Control**: Complete customization of your agent systems

Start building reliable AI agents today! 🤖✨

