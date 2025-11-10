# 🚀 Deploy to GitHub & Render - Step by Step

## ✅ CONFIRMATION: System is 100% Ready

### ✅ Autonomy: 100% AUTONOMOUS
- Scheduler runs continuously
- Executes automatically at 10:00 AM EST daily
- No manual intervention required

### ✅ Fund Usage: 100% UTILIZATION
- Uses 100% of available buying power
- Changed from 95% to 100%
- Maximum capital deployment

### ✅ Position Management: AUTO-SELL BEFORE BUY
- Closes ALL positions before purchasing
- Ensures 100% funds available each day
- Fresh start every trading day

---

## 📤 STEP 1: Push to GitHub

### Initialize Git Repository

```bash
cd "/Users/isaaccohen/Documents/ManyMangoes/MangoMagic/Apps/Trader Bots/MangoTrades V3"

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "MangoTrades V3 - Fully Autonomous 30-Minute Momentum Strategy

- 100% autonomous operation
- Uses 100% of available funds
- Auto-sells all positions before new purchases
- 1% stop-loss on all positions
- Runs daily at 10:00 AM EST"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/mangotrades-v3.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Verify GitHub Upload

Check that these files are in your repository:
- ✅ All Python files (.py)
- ✅ `render.yaml`
- ✅ `Procfile`
- ✅ `requirements.txt`
- ✅ `Stock_list.csv`
- ✅ `static/index.html`
- ✅ Documentation files

**IMPORTANT:** Verify `.env` is NOT in repository (it's in `.gitignore`)

---

## ☁️ STEP 2: Deploy to Render

### Option A: Using Blueprint (Recommended - Auto-detects render.yaml)

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Sign in or create account

2. **Create Blueprint**
   - Click "New +" → "Blueprint"
   - Connect your GitHub account
   - Select repository: `mangotrades-v3`

3. **Render Auto-Detection**
   - Render will automatically detect `render.yaml`
   - It will create:
     - Web Service (API + Dashboard)
     - Worker Service (Scheduler)
     - PostgreSQL Database

4. **Add Environment Variables**
   - Go to each service → Environment
   - Add these variables:

   **For Web Service:**
   ```
   ALPACA_API_KEY=<your_alpaca_api_key>
   ALPACA_SECRET_KEY=<your_alpaca_secret_key>
   ALPACA_BASE_URL=https://paper-api.alpaca.markets
   GEMINI_API_KEY=<your_gemini_api_key>
   FLASK_ENV=production
   FLASK_DEBUG=false
   ```

   **For Worker Service (Scheduler):**
   ```
   ALPACA_API_KEY=<your_alpaca_api_key>
   ALPACA_SECRET_KEY=<your_alpaca_secret_key>
   ALPACA_BASE_URL=https://paper-api.alpaca.markets
   GEMINI_API_KEY=<your_gemini_api_key>
   DATABASE_URL=<from_postgres_database>
   FLASK_ENV=production
   ```

   **Get DATABASE_URL:**
   - Go to PostgreSQL database in Render
   - Copy "Internal Database URL"
   - Add to Worker Service environment variables

5. **Deploy**
   - Click "Apply" or "Create"
   - Render will build and deploy automatically
   - Monitor build logs

### Option B: Manual Service Creation

If Blueprint doesn't work:

1. **Create PostgreSQL Database**
   - New + → PostgreSQL
   - Name: `mangotrades-db`
   - Plan: Free
   - Copy Internal Database URL

2. **Create Web Service**
   - New + → Web Service
   - Connect GitHub repo
   - Settings:
     - Name: `mangotrades-api`
     - Environment: Python 3
     - Build: `pip install -r requirements.txt && python -c "from database import init_db; init_db()"`
     - Start: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
   - Add environment variables (see above)

3. **Create Worker Service**
   - New + → Background Worker
   - Connect GitHub repo
   - Settings:
     - Name: `mangotrades-scheduler`
     - Environment: Python 3
     - Build: `pip install -r requirements.txt && python -c "from database import init_db; init_db()"`
     - Start: `python run_scheduler.py`
   - Add environment variables + DATABASE_URL

---

## ✅ STEP 3: Verify Deployment

### Check Web Service
1. Wait for build to complete (5-10 minutes)
2. Visit your web service URL: `https://mangotrades-api.onrender.com`
3. Should see dashboard
4. Test API: `https://mangotrades-api.onrender.com/api/health`

### Check Worker Service
1. Go to Worker Service → Logs
2. Should see:
   ```
   🚀 MangoTrades V3 - 30-Minute Momentum Strategy Scheduler
   ✅ 100% AUTONOMOUS - No manual intervention required
   Scheduler is running...
   ```

### Check Database
1. Go to PostgreSQL → Connect
2. Verify tables are created
3. Check connection string is correct

---

## 🎯 STEP 4: Test Strategy

### Manual Test (Before Market Hours)

```bash
# Via API
curl -X POST https://your-app.onrender.com/api/strategy/analyze

# Should return qualifying stocks (if any)
```

### Wait for 10:00 AM EST

The scheduler will automatically:
1. Close all positions
2. Analyze stocks
3. Purchase qualifying stocks
4. Set stop-loss orders

---

## 📊 Monitoring

### View Logs
- **Web Service Logs:** Render Dashboard → Web Service → Logs
- **Worker Logs:** Render Dashboard → Worker Service → Logs
- **Database Metrics:** Render Dashboard → Database → Metrics

### Check Execution
- Logs will show daily execution at 10:00 AM EST
- View positions in dashboard
- Check trades in API: `/api/trades`

---

## 🔧 Troubleshooting

### Build Fails
- Check build logs
- Verify Python version (3.11.0)
- Check dependencies in requirements.txt

### Worker Not Running
- Check worker service is running
- Verify environment variables
- Check DATABASE_URL is set

### Strategy Not Executing
- Verify scheduler is running (check logs)
- Check timezone settings
- Ensure market is open (9:30 AM - 4:00 PM EST)

### Database Connection Issues
- Verify DATABASE_URL format
- Check PostgreSQL is running
- Ensure URL uses `postgresql://` not `postgres://`

---

## ✅ DEPLOYMENT CHECKLIST

- [ ] Code pushed to GitHub
- [ ] Repository is public or Render has access
- [ ] Environment variables added to Render
- [ ] Web service deployed and running
- [ ] Worker service deployed and running
- [ ] PostgreSQL database created
- [ ] DATABASE_URL added to worker
- [ ] Logs show scheduler running
- [ ] Dashboard accessible
- [ ] API endpoints responding

---

## 🎉 SUCCESS!

Once deployed:
- ✅ System runs 100% autonomously
- ✅ Executes daily at 10:00 AM EST
- ✅ Uses 100% of available funds
- ✅ Sells all positions before purchasing
- ✅ Sets stop-loss on all purchases

**Your trading bot is live!** 🚀📈

---

## 📝 Quick Commands

```bash
# Check deployment status
curl https://your-app.onrender.com/api/health

# View account info
curl https://your-app.onrender.com/api/account

# Check positions
curl https://your-app.onrender.com/api/positions

# Manual strategy execution (if needed)
curl -X POST https://your-app.onrender.com/api/strategy/execute
```

---

**Ready to deploy! Follow the steps above.** 🚀

