# GitHub Repository Setup

## Initial Setup

### 1. Create GitHub Repository

1. Go to [GitHub](https://github.com/new)
2. Repository name: `mangotrades-v3`
3. Description: "AI-Powered Stock Trading Platform"
4. Choose Public or Private
5. **Don't** initialize with README (we already have one)
6. Click "Create repository"

### 2. Push Your Code

```bash
# Navigate to your project directory
cd "/Users/isaaccohen/Documents/ManyMangoes/MangoMagic/Apps/Trader Bots/MangoTrades V3"

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: MangoTrades V3 - AI-Powered Trading Platform"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/mangotrades-v3.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 3. Verify Upload

- Check that `.env` is **NOT** in the repository (it's in `.gitignore`)
- Verify all Python files are uploaded
- Check that `Stock_list.csv` is included
- Ensure `render.yaml` and `Procfile` are present

## Repository Secrets (Optional)

If you want to use GitHub Actions for deployment:

1. Go to your repository → Settings → Secrets and variables → Actions
2. Add these secrets:
   - `RENDER_SERVICE_ID` - Your Render service ID
   - `RENDER_API_KEY` - Your Render API key

## File Structure on GitHub

Your repository should have:

```
mangotrades-v3/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── static/
│   └── index.html
├── .gitignore
├── .env.example
├── Procfile
├── render.yaml
├── runtime.txt
├── requirements.txt
├── README.md
├── DEPLOYMENT.md
├── QUICKSTART.md
├── GITHUB_SETUP.md
├── SYSTEM_OVERVIEW.md
├── Stock_list.csv
├── app.py
├── config.py
├── database.py
├── stock_checker.py
├── alpaca_client.py
├── ai_decision.py
├── scheduler.py
├── run_scheduler.py
└── start.sh
```

## Important Notes

### ✅ DO Commit:
- All Python files
- Configuration files (`.env.example`, not `.env`)
- Documentation files
- `Stock_list.csv`
- `render.yaml` and `Procfile`
- `.gitignore`

### ❌ DON'T Commit:
- `.env` file (contains secrets)
- `*.db` files (database files)
- `__pycache__/` directories
- Virtual environment (`venv/`)

## Updating Repository

After making changes:

```bash
git add .
git commit -m "Your update description"
git push origin main
```

## Branching Strategy (Optional)

For production deployments:

```bash
# Create development branch
git checkout -b development

# Make changes
git add .
git commit -m "Development changes"

# Merge to main when ready
git checkout main
git merge development
git push origin main
```

## GitHub Actions (CI/CD)

The included `.github/workflows/deploy.yml` will automatically deploy to Render when you push to `main` branch.

To enable:
1. Add secrets in GitHub repository settings
2. Push to main branch
3. Check Actions tab for deployment status

---

**Your code is now on GitHub!** 🎉

Next step: Deploy to Render (see `DEPLOYMENT.md`)

