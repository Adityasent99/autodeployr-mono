# autodeployr-mono

This repository contains:
- `flask-demo/` (Backend - Flask)
- `nextjs-demo/` (Frontend - Next.js)

## Running Flask (local dev)

cat > .gitignore << 'EOF'

.DS_Store

__pycache__/
*.pyc
*.pyo
*.pyd
.venv/
venv/
.env
.env.*
*.sqlite3

node_modules/
.next/
out/
.env.local
.env.*.local


*.log
