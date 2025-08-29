#!/usr/bin/env python3
"""
ITBP Fake Account Detection System - Final Deployment Script
This script creates the complete project structure and deploys everything
"""

import os
import sys
import json
import subprocess
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

class ITBPSystemDeployment:
    def __init__(self):
        self.project_name = "itbp-fake-account-system"
        self.base_dir = Path.cwd() / self.project_name
        self.success_count = 0
        self.total_steps = 10
        
    def print_header(self):
        header = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ITBP FAKE ACCOUNT DETECTION SYSTEM                        ║
║                         ONE-CLICK DEPLOYMENT                                ║
║                                                                              ║
║  🛡 AI-Powered Social Media Security Platform                               ║
║  🔗 Stacks Blockchain Integration                                           ║
║  📊 Real-time Analytics and Reporting                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(header)
        print(f"Deployment Target: {self.base_dir}")
        print("-" * 80)
    
    def step(self, message):
        """Print step progress"""
        self.success_count += 1
        print(f"[{self.success_count}/{self.total_steps}] {message}")
    
    def create_project_structure(self):
        """Create complete project directory structure"""
        self.step("Creating project structure...")
        
        directories = [
            "frontend",
            "backend", 
            "smart-contract",
            "config",
            "scripts",
            "tests",
            "database",
            "docs",
            "logs"
        ]
        
        self.base_dir.mkdir(exist_ok=True)
        
        for dir_name in directories:
            (self.base_dir / dir_name).mkdir(exist_ok=True)
        
        print(f"   ✅ Created project structure in {self.base_dir}")
    
    def create_frontend_files(self):
        """Create frontend HTML file"""
        self.step("Creating frontend files...")
        
        # The frontend file content from the artifact above
        frontend_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ITBP Fake Account Detection System</title>
    <!-- Frontend content would be inserted here -->
    <script>
        // Note: Complete frontend code available in the integration guide
        console.log("ITBP Frontend Loading...");
        document.addEventListener('DOMContentLoaded', function() {
            document.body.innerHTML = `
                <div style="text-align: center; margin-top: 100px; font-family: Arial, sans-serif;">
                    <h1>🛡 ITBP Fake Account Detection System</h1>
                    <p>Frontend is ready! Please refer to the complete HTML file in the integration guide.</p>
                    <p>Backend API: <a href="http://localhost:5000/health">http://localhost:5000/health</a></p>
                </div>
            `;
        });
    </script>
</head>
<body>
    <div>Loading ITBP System...</div>
</body>
</html>'''
        
        frontend_path = self.base_dir / "frontend" / "index.html"
        frontend_path.write_text(frontend_content)
        print("   ✅ Created frontend/index.html (placeholder)")
    
    def create_backend_files(self):
        """Create backend Python files"""
        self.step("Creating backend files...")
        
        # Simplified backend for deployment
        backend_content = '''#!/usr/bin/env python3
"""
ITBP Fake Account Detection System - Backend API
Simplified version for deployment - see integration guide for complete version
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
import os
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'system': 'ITBP Fake Account Detection'
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_account():
    data = request.json
    # Simulate ML analysis
    fake_prob = 0.75 if 'fake' in data.get('username', '').lower() else 0.25
    
    return jsonify({
        'success': True,
        'analysis': {
            'fake_probability': fake_prob,
            'risk_level': 'high' if fake_prob > 0.7 else 'medium' if fake_prob > 0.4 else 'low',
            'confidence': 0.85,
            'detection_reasons': ['Analysis complete - see integration guide for full ML implementation']
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify({
        'total_analyzed': 156,
        'fake_detected': 23,
        'reports_sent': 18,
        'blockchain_records': 15
    })

if __name__ == '__main__':
    print("ITBP Backend API Starting...")
    print("Complete backend implementation available in integration guide")
    app.run(host='0.0.0.0', port=5000, debug=True)
'''
        
        backend_path = self.base_dir / "backend" / "backend_server.py"
        backend_path.write_text(backend_content)
        print("   ✅ Created backend/backend_server.py")
    
    def create_smart_contract(self):
        """Create Clarity smart contract"""
        self.step("Creating smart contract...")
        
        # Copy the Clarity contract from the document
        contract_content = ''';; ITBP Fake Account Registry - Clarity Smart Contract
;; Smart contract for recording fake social media accounts on Stacks blockchain

;; Constants
(define-constant CONTRACT_OWNER tx-sender)
(define-constant ERR_UNAUTHORIZED (err u100))
(define-constant ERR_INVALID_RISK_SCORE (err u101))
(define-constant ERR_EMPTY_FIELDS (err u102))

;; Data structures
(define-map fake-account-reports
  { report-id: (string-ascii 64) }
  {
    platform: (string-ascii 20),
    username: (string-ascii 50),
    risk-score: uint,
    evidence: (string-ascii 500),
    timestamp: uint,
    reporter: principal,
    is-verified: bool,
    is-action-taken: bool,
    block-height: uint
  }
)

;; Public functions
(define-public (report-fake-account 
    (platform (string-ascii 20))
    (username (string-ascii 50))
    (risk-score uint)
    (evidence (string-ascii 500))
    (report-id (string-ascii 64)))
  (begin
    (asserts! (<= risk-score u100) ERR_INVALID_RISK_SCORE)
    (asserts! (> (len platform) u0) ERR_EMPTY_FIELDS)
    (asserts! (> (len username) u0) ERR_EMPTY_FIELDS)
    
    (map-set fake-account-reports
      { report-id: report-id }
      {
        platform: platform,
        username: username,
        risk-score: risk-score,
        evidence: evidence,
        timestamp: stacks-block-height,
        reporter: tx-sender,
        is-verified: (>= risk-score u70),
        is-action-taken: false,
        block-height: stacks-block-height
      })
    
    (print {
      event: "fake-account-reported",
      platform: platform,
      username: username,
      risk-score: risk-score,
      reporter: tx-sender
    })
    
    (ok true)))

;; Read-only functions
(define-read-only (get-report (report-id (string-ascii 64)))
  (map-get? fake-account-reports { report-id: report-id }))
'''
        
        contract_path = self.base_dir / "smart-contract" / "fake-account-registry.clar"
        contract_path.write_text(contract_content)
        print("   ✅ Created smart-contract/fake-account-registry.clar")
    
    def create_configuration_files(self):
        """Create configuration files"""
        self.step("Creating configuration files...")
        
        # Environment configuration
        env_content = '''# ITBP Fake Account Detection System Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=itbp_secure_key_2024

# Database Configuration
DATABASE_URL=sqlite:///database/blockchain_records.db

# Stacks Blockchain Configuration
STACKS_API_URL=https://api.testnet.hiro.so
STACKS_NETWORK=testnet
STACKS_CONTRACT_ADDRESS=ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM
STACKS_CONTRACT_NAME=fake-account-registry
STACKS_PRIVATE_KEY=your_private_key_here

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
'''
        
        env_path = self.base_dir / "config" / ".env"
        env_path.write_text(env_content)
        
        # API Configuration
        config_content = {
            "agencies": {
                "itbp": {
                    "name": "Indo-Tibetan Border Police",
                    "email": "itbp.cybersecurity@gov.in",
                    "priority_threshold": 0.6
                }
            },
            "stacks": {
                "network": "testnet",
                "api_url": "https://api.testnet.hiro.so"
            }
        }
        
        config_path = self.base_dir / "config" / "config.json"
        config_path.write_text(json.dumps(config_content, indent=2))
        
        print("   ✅ Created configuration files")
    
    def create_database(self):
        """Initialize SQLite database"""
        self.step("Creating database...")
        
        db_path = self.base_dir / "database" / "blockchain_records.db"
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Create main tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fake_account_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                username TEXT NOT NULL,
                risk_score REAL NOT NULL,
                evidence TEXT,
                tx_hash TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                report_id TEXT UNIQUE,
                agency TEXT,
                priority TEXT,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_stats (
                id INTEGER PRIMARY KEY,
                total_analyzed INTEGER DEFAULT 0,
                fake_detected INTEGER DEFAULT 0,
                reports_sent INTEGER DEFAULT 0,
                blockchain_records INTEGER DEFAULT 0,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert initial stats
        cursor.execute('''
            INSERT OR IGNORE INTO system_stats (id, total_analyzed, fake_detected, reports_sent)
            VALUES (1, 0, 0, 0)
        ''')
        
        conn.commit()
        conn.close()
        
        print(f"   ✅ Created database: {db_path}")
    
    def create_requirements(self):
        """Create requirements.txt"""
        self.step("Creating requirements file...")
        
        requirements = '''flask==2.3.3
flask-cors==4.0.0
pandas==2.1.0
numpy==1.24.3
scikit-learn==1.3.0
joblib==1.3.2
requests==2.31.0
python-dotenv==1.0.0
gunicorn==21.2.0
pytest==7.4.2
'''
        
        req_path = self.base_dir / "requirements.txt"
        req_path.write_text(requirements)
        
        print("   ✅ Created requirements.txt")
    
    def create_startup_scripts(self):
        """Create startup scripts"""
        self.step("Creating startup scripts...")
        
        # Windows batch file
        windows_script = '''@echo off
echo ITBP Fake Account Detection System
echo ==================================

echo Installing dependencies...
pip install -r requirements.txt

echo Starting system...
cd backend
start "ITBP Backend" python backend_server.py

echo System ready!
echo Backend: http://localhost:5000
echo Frontend: Open frontend/index.html in browser

timeout /t 3
start ../frontend/index.html

pause
'''
        
        windows_path = self.base_dir / "scripts" / "start_windows.bat"
        windows_path.write_text(windows_script)
        
        # Unix shell script
        unix_script = '''#!/bin/bash
echo "ITBP Fake Account Detection System"
echo "=================================="

echo "Installing dependencies..."
pip3 install -r requirements.txt

echo "Starting system..."
cd backend
python3 backend_server.py &
BACKEND_PID=$!

echo "System ready!"
echo "Backend: http://localhost:5000"
echo "Frontend: Open frontend/index.html in browser"

sleep 3
if command -v xdg-open > /dev/null; then
    xdg-open ../frontend/index.html
elif command -v open > /dev/null; then
    open ../frontend/index.html
fi

echo "Press Ctrl+C to stop system"
trap 'kill $BACKEND_PID; exit' INT
wait
'''
        
        unix_path = self.base_dir / "scripts" / "start_unix.sh"
        unix_path.write_text(unix_script)
        
        # Make Unix script executable
        if os.name != 'nt':
            os.chmod(unix_path, 0o755)
        
        print("   ✅ Created startup scripts")
    
    def create_documentation(self):
        """Create documentation"""
        self.step("Creating documentation...")
        
        readme_content = f'''# ITBP Fake Account Detection System

## Overview
Advanced AI-powered social media security platform with Stacks blockchain integration.

## Quick Start

### Windows
1. Double-click `scripts/start_windows.bat`
2. Wait for system to start
3. Frontend will open automatically

### Linux/Mac
1. Run `./scripts/start_unix.sh`
2. Wait for system to start
3. Open `frontend/index.html` in browser

### Manual Start
```bash
# Install dependencies
pip install -r requirements.txt

# Start backend
cd backend
python backend_server.py

# Open frontend/index.html in browser
```

## System URLs
- Backend API: http://localhost:5000
- Health Check: http://localhost:5000/health
- Frontend: Open `frontend/index.html`

## Project Structure
```
{self.project_name}/
├── frontend/           # Web interface
├── backend/           # Python API server
├── smart-contract/    # Clarity smart contract
├── config/           # Configuration files
├── scripts/          # Startup scripts
├── database/         # SQLite database
└── docs/            # Documentation
```

## Features
- 🤖 AI-powered fake account detection
- 🔗 Stacks blockchain integration
- 📊 Real-time analytics
- 🏛 Multi-agency reporting
- 🛡 Security monitoring

## Support
Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
For issues, refer to the complete integration guide.
'''
        
        readme_path = self.base_dir / "README.md"
        readme_path.write_text(readme_content)
        
        print("   ✅ Created README.md")
    
    def run_final_checks(self):
        """Run final system checks"""
        self.step("Running final system checks...")
        
        # Check Python installation
        try:
            result = subprocess.run([sys.executable, '--version'], 
                                  capture_output=True, text=True)
            python_version = result.stdout.strip()
            print(f"   ✅ Python: {python_version}")
        except:
            print("   ⚠  Python check failed")
        
        # Check required directories
        required_dirs = ['frontend', 'backend', 'smart-contract', 'database']
        for dir_name in required_dirs:
            dir_path = self.base_dir / dir_name
            if dir_path.exists():
                print(f"   ✅ Directory: {dir_name}/")
            else:
                print(f"   ❌ Missing: {dir_name}/")
        
        # Check key files
        key_files = [
            'frontend/index.html',
            'backend/backend_server.py', 
            'smart-contract/fake-account-registry.clar',
            'requirements.txt',
            'README.md'
        ]
        
        for file_path in key_files:
            full_path = self.base_dir / file_path
            if full_path.exists():
                print(f"   ✅ File: {file_path}")
            else:
                print(f"   ❌ Missing: {file_path}")
    
    def print_completion_message(self):
        """Print final completion message"""
        completion_msg = f'''
╔══════════════════════════════════════════════════════════════════════════════╗
║                           DEPLOYMENT COMPLETED! 🎉                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

📁 Project created at: {self.base_dir}

🚀 Quick Start:
   Windows: Double-click scripts/start_windows.bat
   Linux/Mac: ./scripts/start_unix.sh

🌐 System URLs:
   • Backend API: http://localhost:5000
   • Health Check: http://localhost:5000/health  
   • Frontend: Open frontend/index.html in browser

📋 Next Steps:
   1. Navigate to project directory: cd {self.project_name}
   2. Start the system using provided scripts
   3. Configure .env file with your Stacks credentials
   4. Deploy smart contract to Stacks testnet
   5. Refer to integration guide for complete implementation

📞 Support:
   • Check README.md for basic usage
   • See integration guide for complete feature implementation
   • GitHub issues for technical problems

🎯 System Features Ready:
   ✅ Basic project structure
   ✅ Database initialization
   ✅ API endpoints (basic)
   ✅ Frontend interface (placeholder)
   ✅ Smart contract code
   
⚠  Next Phase (See Integration Guide):
   • Complete ML implementation
   • Full Stacks blockchain integration
   • Production security features
   • Advanced monitoring and reporting

Happy detecting! 🛡'''
        
    def deploy(self):
        """Run complete deployment"""
        try:
            self.print_header()
            
            self.create_project_structure()
            self.create_frontend_files()
            self.create_backend_files()
            self.create_smart_contract()
            self.create_configuration_files()
            self.create_database()
            self.create_requirements()
            self.create_startup_scripts()
            self.create_documentation()
            self.run_final_checks()
            
            self.print_completion_message()
            
            return True
            
        except Exception as e:
            print(f"\n❌ Deployment failed: {e}")
            print("Please check the error and try again.")
            return False
        except KeyboardInterrupt:
            print("\n❌ Deployment interrupted by user")
            return False

def main():
    """Main deployment function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("ITBP Fake Account Detection System Deployment")
        print("Usage: python deploy.py")
        print("This script creates the complete project structure and basic files.")
        return
    
    deployer = ITBPSystemDeployment()
    success = deployer.deploy()
    
    if success:
        print(f"\nTo start the system:")
        print(f"cd {deployer.project_name}")
        if os.name == 'nt':
            print("scripts\\start_windows.bat")
        else:
            print("./scripts/start_unix.sh")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()