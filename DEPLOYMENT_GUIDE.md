# 🚀 Presentation Evaluation Tool - Deployment Guide

## Overview
This tool evaluates AI-generated presentations using Claude API. It provides:
- Web interface for uploading presentations
- Automated evaluation using Claude
- Persistent database storage
- Downloadable PDF reports
- Cost tracking per evaluation
- Customizable rubric

---

## 📋 Prerequisites

1. **Computer with:**
   - Internet connection
   - Web browser (Chrome, Firefox, Safari)
   - Terminal/Command Prompt access

2. **Accounts you'll need (all free tiers available):**
   - Anthropic API key (get from console.anthropic.com)
   - Render.com account (for deployment) OR
   - Railway.app account (alternative)

---

## 🛠️ Option 1: Deploy to Render.com (Recommended - Easiest)

### Step 1: Get Your Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign in or create account
3. Click "API Keys" in sidebar
4. Click "Create Key"
5. Copy the key (starts with `sk-ant-`)
6. **SAVE THIS KEY** - you won't see it again

### Step 2: Prepare Your Files

1. Download all files from this folder to your computer:
   - `app.py`
   - `requirements.txt`
   - `Procfile`
   - `runtime.txt`
   - `.gitignore`
   - `templates/index.html`

2. Create this folder structure on your computer:
   ```
   pres-eval-tool/
   ├── app.py
   ├── requirements.txt
   ├── Procfile
   ├── runtime.txt
   ├── .gitignore
   └── templates/
       └── index.html
   ```

### Step 3: Create GitHub Repository

1. Go to https://github.com/
2. Click "New repository"
3. Name it: `presentation-evaluation-tool`
4. Select "Public" (free hosting requires public repo)
5. Click "Create repository"

### Step 4: Upload Files to GitHub

**Option A: Using GitHub Website (Easier)**
1. In your new repository, click "uploading an existing file"
2. Drag and drop all files EXCEPT the templates folder
3. Click "Commit changes"
4. Click "Add file" > "Create new file"
5. Type `templates/index.html` as filename
6. Paste the HTML content
7. Click "Commit changes"

**Option B: Using Git (If you know Git)**
```bash
cd pres-eval-tool
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR-USERNAME/presentation-evaluation-tool.git
git push -u origin main
```

### Step 5: Deploy to Render

1. Go to https://render.com/
2. Sign up/Login (use GitHub to sign in - easiest)
3. Click "New" > "Web Service"
4. Connect your GitHub repository
5. Select `presentation-evaluation-tool`
6. Configure:
   - **Name**: `pres-eval-tool` (or any name)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free

7. Click "Advanced" > "Add Environment Variable":
   - **Key**: `ANTHROPIC_API_KEY`
   - **Value**: Your API key from Step 1
   
   Add another:
   - **Key**: `SECRET_KEY`
   - **Value**: Any random string (e.g., `my-secret-key-12345`)

8. Click "Create Web Service"

### Step 6: Wait for Deployment

- Render will build and deploy (takes 5-10 minutes)
- Watch the logs for progress
- When you see "Service is live", it's ready!
- Your URL will be: `https://pres-eval-tool.onrender.com`

### Step 7: Test Your Tool

1. Go to your Render URL
2. You should see the Presentation Evaluation Tool interface
3. Try uploading a presentation to test

---

## 🛠️ Option 2: Deploy to Railway.app (Alternative)

### Step 1-4: Same as Render (get API key, prepare files, create GitHub repo)

### Step 5: Deploy to Railway

1. Go to https://railway.app/
2. Sign up with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose `presentation-evaluation-tool`
6. Railway will auto-detect settings

### Step 6: Add Environment Variables

1. Click on your service
2. Go to "Variables" tab
3. Add:
   - `ANTHROPIC_API_KEY` = your key
   - `SECRET_KEY` = any random string

### Step 7: Get Your URL

1. Go to "Settings" tab
2. Click "Generate Domain"
3. Your URL will be: `https://your-project.up.railway.app`

---

## 🖥️ Option 3: Run Locally (For Testing)

### Step 1: Install Python

**Windows:**
1. Download Python 3.11 from python.org
2. Run installer, CHECK "Add Python to PATH"
3. Click "Install Now"

**Mac:**
```bash
brew install python@3.11
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install python3.11 python3-pip
```

### Step 2: Setup Project

```bash
# Navigate to your project folder
cd path/to/pres-eval-tool

# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Set Environment Variables

**Windows:**
```bash
set ANTHROPIC_API_KEY=your-api-key-here
set SECRET_KEY=any-random-string
```

**Mac/Linux:**
```bash
export ANTHROPIC_API_KEY=your-api-key-here
export SECRET_KEY=any-random-string
```

### Step 4: Run Application

```bash
python app.py
```

Open browser to: http://localhost:5000

---

## 📝 How to Use the Tool

### 1. Evaluate a Presentation

1. Go to "New Evaluation" tab
2. Upload:
   - **JSON file**: The metadata/input file from your system
   - **PDF file**: The generated presentation
   - **Additional files** (optional): Source Excel, docs, etc.
3. Click "Evaluate Presentation"
4. Wait 30-60 seconds for Claude to analyze
5. See results in "Evaluated Presentations" tab

### 2. View Past Evaluations

1. Click "Evaluated Presentations" tab
2. See table with all evaluations:
   - Date
   - User outline preview
   - Preferences used
   - Doc type
   - Score
   - Category (Excellent/Good/etc.)
   - Cost of evaluation
   - Download report button
3. Click "Download" to get PDF report

### 3. Customize Rubric

1. Click "Rubric Settings" tab
2. Adjust weights for each dimension
3. Total must equal 100%
4. Click "Save Rubric Changes"
5. New evaluations will use updated rubric

---

## 💰 Cost Management

### Understanding Costs

- Each evaluation calls Claude Sonnet 4
- Cost per evaluation: ~$0.01 - $0.05 (depends on presentation size)
- The tool tracks and displays exact cost per evaluation
- View total spend in the dashboard

### Cost Tracking

- **Dashboard shows**: Total evaluations, average score, total cost
- **Table shows**: Cost per individual evaluation
- **Reports include**: Token usage (input/output)

### Staying Within Budget

1. Set Anthropic API usage limits in console.anthropic.com
2. Monitor costs in the dashboard
3. Free tier includes $5 credit (100-500 evaluations)

---

## 🔧 Troubleshooting

### "API Key Error"
- Check that ANTHROPIC_API_KEY is set correctly
- Verify key starts with `sk-ant-`
- Regenerate key in Anthropic console if needed

### "File Upload Fails"
- Check file size (max 50MB)
- Ensure JSON is valid format
- Ensure PDF is not corrupted

### "Database Error"
- Database auto-creates on first run
- On Render: Use persistent disk (see below)

### "Can't Access After Deployment"
- Wait 5-10 minutes for first deployment
- Check Render/Railway logs for errors
- Ensure environment variables are set

---

## 💾 Making Data Persistent on Render

**Important**: By default, Render free tier doesn't persist data between deployments.

### Option 1: Add Persistent Disk (Recommended)

1. In Render dashboard, go to your service
2. Click "Environment" tab
3. Scroll to "Disk"
4. Click "Add Disk"
5. Set:
   - **Name**: `data`
   - **Mount Path**: `/opt/render/project/src/data`
   - **Size**: 1 GB (free)
6. Update `app.py` line 28:
   ```python
   conn = sqlite3.connect('/opt/render/project/src/data/evaluations.db')
   ```
   Do this for ALL `sqlite3.connect()` calls in the file

### Option 2: Use External Database (Advanced)

1. Create PostgreSQL database on Render
2. Update code to use PostgreSQL instead of SQLite
3. (Instructions available if needed)

---

## 🔐 Security Best Practices

1. **Never commit API keys to GitHub**
   - Use environment variables only
   - .gitignore already excludes sensitive files

2. **Use Strong SECRET_KEY**
   - Generate random string: `python -c "import secrets; print(secrets.token_hex(32))"`

3. **Restrict Access** (if needed)
   - Add authentication (can provide code)
   - Use Render's IP allowlist

---

## 📊 Feature Checklist

✅ **Core Features Implemented:**
- [x] Upload JSON + PDF for evaluation
- [x] Claude API integration
- [x] Persistent SQLite database
- [x] Downloadable PDF reports
- [x] Cost tracking per evaluation
- [x] Customizable rubric
- [x] Dashboard with statistics
- [x] Table view of all evaluations
- [x] Progress indicators
- [x] English reports (regardless of presentation language)

✅ **Data Persistence:**
- [x] SQLite database stores all evaluations
- [x] Survives server restarts (with persistent disk)
- [x] No session-based storage

✅ **Cost Tracking:**
- [x] Per-evaluation cost display
- [x] Total cost in dashboard
- [x] Token usage tracking

---

## 🎯 Quick Start Checklist

- [ ] Get Anthropic API key
- [ ] Create GitHub repository
- [ ] Upload files to GitHub
- [ ] Sign up for Render.com
- [ ] Deploy to Render
- [ ] Add environment variables
- [ ] Wait for deployment
- [ ] Test with sample presentation
- [ ] (Optional) Add persistent disk

---

## 📞 Need Help?

If you encounter issues:

1. Check Render logs: Click "Logs" tab in Render dashboard
2. Verify environment variables are set
3. Test locally first to isolate deployment issues
4. Check that all files are uploaded correctly

---

## 🚀 You're Ready!

Your presentation evaluation tool is now:
- ✅ Deployed and accessible via web URL
- ✅ Connected to Claude API
- ✅ Storing data persistently
- ✅ Tracking costs
- ✅ Ready to evaluate presentations

**Next Steps:**
1. Bookmark your Render URL
2. Share with your team
3. Start evaluating presentations!

---

## 💡 Pro Tips

1. **Batch Processing**: Upload multiple presentations in sequence
2. **Cost Optimization**: Monitor dashboard regularly
3. **Rubric Tuning**: Adjust weights based on your priorities
4. **Report Sharing**: Download PDFs and share via email/Slack
5. **Regular Backups**: Download evaluation data periodically

Enjoy your new presentation evaluation tool! 🎉
