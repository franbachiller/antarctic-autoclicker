#!/bin/bash

# Antarctic Backend Deployment Script
echo "🚀 Antarctic Backend Deployment"
echo "================================"

echo "📋 Steps to deploy:"
echo "1. Create a new repository on GitHub"
echo "2. Copy all files from this directory to the new repository"
echo "3. Push to GitHub"
echo "4. Connect to Vercel as a new project"
echo "5. Set environment variable: ADMIN_KEY=ADMIN_KEY_REMOVED"
echo "6. Connect Vercel Postgres database"
echo "7. Run the SQL schema from schema.sql"

echo ""
echo "🔧 Manual deployment:"
echo "1. Go to https://github.com/new"
echo "2. Create repository: antarctic-backend"
echo "3. Copy all files from backend-setup/ to the new repo"
echo "4. Run: git add . && git commit -m 'Initial backend setup' && git push"
echo "5. Connect to Vercel: https://vercel.com/new"
echo "6. Set ADMIN_KEY=ADMIN_KEY_REMOVED in environment variables"
echo "7. Connect Postgres database in Storage tab"
echo "8. Run SQL from schema.sql in database console"

echo ""
echo "✅ After deployment, test with:"
echo "curl -H 'X-Admin-Key: ADMIN_KEY_REMOVED' https://your-backend.vercel.app/api/admin/stats"
