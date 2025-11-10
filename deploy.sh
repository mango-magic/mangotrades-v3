#!/bin/bash

# MangoTrades V3 - Deployment Script
# This script helps deploy to GitHub and prepares for Render

echo "🚀 MangoTrades V3 - Deployment Script"
echo "======================================"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git repository already initialized"
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo ""
    echo "📝 Staging all files..."
    git add .
    
    echo ""
    echo "💾 Committing changes..."
    git commit -m "MangoTrades V3 - Fully Autonomous 30-Minute Momentum Strategy

- 100% autonomous operation
- Uses 100% of available funds daily
- Auto-sells all positions before new purchases
- 1% stop-loss on all positions
- Runs daily at 10:00 AM EST"
    
    echo "✅ Changes committed"
else
    echo "✅ No changes to commit"
fi

# Check if remote exists
if git remote get-url origin >/dev/null 2>&1; then
    echo ""
    echo "✅ Remote repository configured"
    echo "   Remote: $(git remote get-url origin)"
    echo ""
    echo "📤 Pushing to GitHub..."
    git push -u origin main
    echo "✅ Code pushed to GitHub!"
else
    echo ""
    echo "⚠️  No remote repository configured"
    echo ""
    echo "To add remote repository, run:"
    echo "  git remote add origin https://github.com/YOUR_USERNAME/mangotrades-v3.git"
    echo "  git branch -M main"
    echo "  git push -u origin main"
fi

echo ""
echo "======================================"
echo "✅ Deployment preparation complete!"
echo ""
echo "Next steps:"
echo "1. Go to https://dashboard.render.com"
echo "2. Click 'New +' → 'Blueprint'"
echo "3. Connect your GitHub repository"
echo "4. Render will auto-detect render.yaml"
echo "5. Add environment variables"
echo "6. Deploy!"
echo ""
echo "See DEPLOY_NOW.md for detailed instructions"

