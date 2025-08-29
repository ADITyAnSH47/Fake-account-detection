# backend_server.py - Updated with Stacks blockchain integration
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
import joblib
import re
import hashlib
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import os
import sqlite3
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StacksBlockchainManager:
    def __init__(self):
        # Stacks blockchain configuration
        self.stacks_api_url = os.getenv('STACKS_API_URL', 'https://api.testnet.hiro.so')
        self.contract_address = os.getenv('STACKS_CONTRACT_ADDRESS', '')
        self.contract_name = os.getenv('STACKS_CONTRACT_NAME', 'fake-account-registry')
        self.private_key = os.getenv('STACKS_PRIVATE_KEY', '')
        
    def call_contract_function(self, function_name, function_args, sender_key):
        """Call a Stacks smart contract function"""
        try:
            # Construct transaction data for Stacks
            tx_data = {
                "contract_address": self.contract_address,
                "contract_name": self.contract_name,
                "function_name": function_name,
                "function_args": function_args,
                "sender": sender_key
            }
            
            # For demo purposes, simulate the transaction
            tx_hash = hashlib.sha256(
                f"{function_name}{json.dumps(function_args)}{datetime.now()}".encode()
            ).hexdigest()
            
            # Store in local database
            self.store_local_record(function_name, function_args, tx_hash)
            
            return {
                'success': True,
                'tx_hash': f"0x{tx_hash}",
                'block_height': np.random.randint(100000, 999999),
                'contract_address': self.contract_address,
                'function_name': function_name
            }
        except Exception as e:
            logger.error(f"Contract call failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def report_fake_account(self, platform, username, risk_score, evidence, report_id, sender_key):
        """Report fake account to Stacks blockchain"""
        function_args = [
            {'type': 'string-ascii', 'value': platform},
            {'type': 'string-ascii', 'value': username},
            {'type': 'uint', 'value': int(risk_score * 100)},  # Convert to 0-100 scale
            {'type': 'string-ascii', 'value': evidence},
            {'type': 'string-ascii', 'value': report_id}
        ]
        
        return self.call_contract_function('report-fake-account', function_args, sender_key)
    
    def verify_report(self, report_id, sender_key):
        """Verify a report on the blockchain"""
        function_args = [
            {'type': 'string-ascii', 'value': report_id}
        ]
        
        return self.call_contract_function('verify-report', function_args, sender_key)
    
    def mark_action_taken(self, report_id, action, sender_key):
        """Mark action taken on a report"""
        function_args = [
            {'type': 'string-ascii', 'value': report_id},
            {'type': 'string-ascii', 'value': action}
        ]
        
        return self.call_contract_function('mark-action-taken', function_args, sender_key)
    
    def get_report(self, report_id):
        """Get report from blockchain (read-only)"""
        try:
            # For demo, retrieve from local database
            conn = sqlite3.connect('blockchain_records.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM fake_account_reports 
                WHERE report_id = ?
            ''', (report_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'success': True,
                    'report': {
                        'platform': result[1],
                        'username': result[2],
                        'risk_score': result[3],
                        'evidence': result[4],
                        'tx_hash': result[5],
                        'timestamp': result[6],
                        'report_id': result[7]
                    }
                }
            else:
                return {'success': False, 'error': 'Report not found'}
        except Exception as e:
            logger.error(f"Get report failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def store_local_record(self, function_name, args, tx_hash):
        """Store blockchain interaction in local database"""
        conn = sqlite3.connect('blockchain_records.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blockchain_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                function_name TEXT,
                args TEXT,
                tx_hash TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        cursor.execute('''
            INSERT INTO blockchain_transactions (function_name, args, tx_hash)
            VALUES (?, ?, ?)
        ''', (function_name, json.dumps(args), tx_hash))
        
        # Also store in fake_account_reports if it's a report function
        if function_name == 'report-fake-account' and len(args) >= 5:
            cursor.execute('''
                INSERT INTO fake_account_reports 
                (platform, username, risk_score, evidence, tx_hash, report_id, agency, priority, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                args[0]['value'],  # platform
                args[1]['value'],  # username
                args[2]['value'] / 100.0,  # risk_score (convert back to 0-1)
                args[3]['value'],  # evidence
                tx_hash,
                args[4]['value'],  # report_id
                'itbp',  # default agency
                'medium',  # default priority
                'recorded'
            ))
        
        conn.commit()
        conn.close()

class MLFakeAccountDetector:
    def __init__(self):
        self.profile_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.network_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.behavior_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def generate_training_data(self, n_samples=1000):
        """Generate synthetic training data for demo purposes"""
        np.random.seed(42)
        
        # Generate fake and real account features
        fake_data = []
        real_data = []
        
        for i in range(n_samples // 2):
            # Fake account characteristics
            fake_features = {
                'followers_count': np.random.exponential(100),
                'following_count': np.random.exponential(500),
                'posts_count': np.random.poisson(5),
                'account_age_days': np.random.exponential(30),
                'profile_pic': np.random.choice([0, 1], p=[0.3, 0.7]),
                'bio_length': np.random.exponential(20),
                'verified': 0,
                'username_digits': np.random.poisson(4),
                'engagement_rate': np.random.exponential(0.01),
                'posting_frequency': np.random.exponential(0.5)
            }
            fake_data.append(list(fake_features.values()) + [1])  # 1 = fake
            
            # Real account characteristics
            real_features = {
                'followers_count': np.random.exponential(500),
                'following_count': np.random.exponential(200),
                'posts_count': np.random.poisson(50),
                'account_age_days': np.random.exponential(365),
                'profile_pic': np.random.choice([0, 1], p=[0.1, 0.9]),
                'bio_length': np.random.normal(80, 30),
                'verified': np.random.choice([0, 1], p=[0.95, 0.05]),
                'username_digits': np.random.poisson(1),
                'engagement_rate': np.random.normal(0.03, 0.01),
                'posting_frequency': np.random.exponential(2)
            }
            real_data.append(list(real_features.values()) + [0])  # 0 = real
        
        # Combine and create DataFrame
        all_data = fake_data + real_data
        columns = ['followers_count', 'following_count', 'posts_count', 'account_age_days',
                  'profile_pic', 'bio_length', 'verified', 'username_digits',
                  'engagement_rate', 'posting_frequency', 'is_fake']
        
        return pd.DataFrame(all_data, columns=columns)
    
    def train_models(self):
        """Train ML models with synthetic data"""
        logger.info("Training ML models...")
        
        # Generate training data
        df = self.generate_training_data(2000)
        
        # Prepare features and target
        X = df.drop('is_fake', axis=1)
        y = df['is_fake']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train classifier
        self.profile_classifier.fit(X_scaled, y)
        
        # Save models
        joblib.dump(self.profile_classifier, 'profile_classifier.pkl')
        joblib.dump(self.scaler, 'feature_scaler.pkl')
        
        self.is_trained = True
        logger.info("ML models trained successfully")
    
    def extract_features_from_account(self, account_data):
        """Extract features from account data"""
        username = account_data.get('username', '')
        bio = account_data.get('bio', '')
        platform = account_data.get('platform', '')
        
        # Extract numerical features
        features = {
            'followers_count': np.random.exponential(300),  # Simulated - in real app, fetch from API
            'following_count': np.random.exponential(250),
            'posts_count': np.random.poisson(20),
            'account_age_days': np.random.exponential(200),
            'profile_pic': 1 if account_data.get('profilePicture') else 0,
            'bio_length': len(bio),
            'verified': 0,  # Simulated
            'username_digits': len(re.findall(r'\d', username)),
            'engagement_rate': np.random.exponential(0.02),
            'posting_frequency': np.random.exponential(1.5)
        }
        
        return features
    
    def analyze_account(self, account_data):
        """Analyze account and predict if it's fake"""
        if not self.is_trained:
            self.train_models()
        
        try:
            # Extract features
            features = self.extract_features_from_account(account_data)
            feature_vector = np.array(list(features.values())).reshape(1, -1)
            
            # Scale features
            feature_vector_scaled = self.scaler.transform(feature_vector)
            
            # Predict
            fake_probability = self.profile_classifier.predict_proba(feature_vector_scaled)[0][1]
            prediction = self.profile_classifier.predict(feature_vector_scaled)[0]
            
            # Generate analysis report
            analysis = {
                'fake_probability': float(fake_probability),
                'is_fake': bool(prediction),
                'risk_level': self.get_risk_level(fake_probability),
                'confidence': float(np.max(self.profile_classifier.predict_proba(feature_vector_scaled))),
                'features': features,
                'detection_reasons': self.get_detection_reasons(features, fake_probability)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Account analysis failed: {e}")
            return {
                'fake_probability': 0.5,
                'is_fake': False,
                'risk_level': 'unknown',
                'confidence': 0.5,
                'features': {},
                'detection_reasons': ['Analysis failed']
            }
    
    def get_risk_level(self, probability):
        """Convert probability to risk level"""
        if probability >= 0.7:
            return 'high'
        elif probability >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def get_detection_reasons(self, features, probability):
        """Generate human-readable detection reasons"""
        reasons = []
        
        if features['username_digits'] > 3:
            reasons.append('Username contains many digits')
        
        if features['bio_length'] < 10:
            reasons.append('Very short or missing bio')
        
        if features['account_age_days'] < 30:
            reasons.append('Recently created account')
        
        if features['followers_count'] < 10:
            reasons.append('Very few followers')
        
        if features['profile_pic'] == 0:
            reasons.append('No profile picture')
        
        if probability > 0.7:
            reasons.append('Multiple suspicious indicators detected')
        
        return reasons if reasons else ['Account appears normal']

# Initialize components
blockchain_manager = StacksBlockchainManager()
ml_detector = MLFakeAccountDetector()

# API Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'blockchain': 'connected' if blockchain_manager.contract_address else 'disconnected'
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_account():
    """Analyze account for fake characteristics"""
    try:
        data = request.json
        
        # Validate input
        required_fields = ['platform', 'username']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Perform ML analysis
        analysis = ml_detector.analyze_account(data)
        
        # Record to blockchain if high risk
        blockchain_result = None
        if analysis['fake_probability'] >= 0.4:
            report_id = f"RPT_{int(datetime.now().timestamp())}"
            blockchain_result = blockchain_manager.report_fake_account(
                platform=data['platform'],
                username=data['username'],
                risk_score=analysis['fake_probability'],
                evidence=f"ML Analysis: {', '.join(analysis['detection_reasons'])}",
                report_id=report_id,
                sender_key=blockchain_manager.private_key
            )
        
        # Update statistics
        update_statistics(analysis)
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'blockchain': blockchain_result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return jsonify({'error': 'Analysis failed', 'details': str(e)}), 500

@app.route('/api/report', methods=['POST'])
def generate_report():
    """Generate official report for agencies"""
    try:
        data = request.json
        
        # Validate input
        required_fields = ['agencyType', 'priority']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Generate report ID
        report_id = f"RPT_{data['agencyType'].upper()}_{int(datetime.now().timestamp())}"
        
        # Create report data
        report_data = {
            'report_id': report_id,
            'agency': data['agencyType'],
            'priority': data['priority'],
            'evidence': data.get('evidence', ''),
            'timestamp': datetime.now().isoformat(),
            'status': 'submitted'
        }
        
        # Store report in database
        store_report(report_data)
        
        # Send email notification (simulated)
        send_report_notification(report_data)
        
        return jsonify({
            'success': True,
            'report_id': report_id,
            'message': f'Report submitted to {data["agencyType"].upper()}',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return jsonify({'error': 'Report generation failed', 'details': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """Get system statistics"""
    try:
        conn = sqlite3.connect('blockchain_records.db')
        cursor = conn.cursor()
        
        # Get basic stats
        cursor.execute('SELECT * FROM system_stats WHERE id = 1')
        stats = cursor.fetchone()
        
        # Get blockchain stats
        cursor.execute('SELECT COUNT(*) FROM blockchain_transactions')
        blockchain_records = cursor.fetchone()[0]
        
        # Get recent reports
        cursor.execute('''
            SELECT COUNT(*) FROM fake_account_reports 
            WHERE timestamp > datetime('now', '-7 days')
        ''')
        recent_reports = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'total_analyzed': stats[1] if stats else 0,
            'fake_detected': stats[2] if stats else 0,
            'reports_sent': stats[3] if stats else 0,
            'blockchain_records': blockchain_records,
            'recent_reports': recent_reports,
            'last_updated': stats[4] if stats else datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Statistics retrieval failed: {e}")
        return jsonify({'error': 'Statistics retrieval failed'}), 500

@app.route('/api/blockchain/records', methods=['GET'])
def get_blockchain_records():
    """Get recent blockchain records"""
    try:
        conn = sqlite3.connect('blockchain_records.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT tx_hash, function_name, timestamp, status
            FROM blockchain_transactions
            ORDER BY timestamp DESC
            LIMIT 10
        ''')
        
        records = []
        for row in cursor.fetchall():
            records.append({
                'tx_hash': row[0],
                'function_name': row[1],
                'timestamp': row[2],
                'status': row[3]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'records': records
        })
        
    except Exception as e:
        logger.error(f"Blockchain records retrieval failed: {e}")
        return jsonify({'error': 'Records retrieval failed'}), 500

# Helper functions
def update_statistics(analysis):
    """Update system statistics"""
    try:
        conn = sqlite3.connect('blockchain_records.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE system_stats 
            SET total_analyzed = total_analyzed + 1,
                fake_detected = fake_detected + ?,
                last_updated = CURRENT_TIMESTAMP
            WHERE id = 1
        ''', (1 if analysis['is_fake'] else 0,))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Statistics update failed: {e}")

def store_report(report_data):
    """Store report in database"""
    try:
        conn = sqlite3.connect('blockchain_records.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO fake_account_reports 
            (report_id, agency, priority, evidence, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            report_data['report_id'],
            report_data['agency'],
            report_data['priority'],
            report_data['evidence'],
            report_data['status']
        ))
        
        # Update stats
        cursor.execute('''
            UPDATE system_stats 
            SET reports_sent = reports_sent + 1,
                last_updated = CURRENT_TIMESTAMP
            WHERE id = 1
        ''')
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Report storage failed: {e}")

def send_report_notification(report_data):
    """Send email notification to agency"""
    # In production, implement actual email sending
    logger.info(f"Report notification sent: {report_data['report_id']} to {report_data['agency']}")

def init_database():
    """Initialize database with required tables"""
    conn = sqlite3.connect('blockchain_records.db')
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fake_account_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT,
            username TEXT,
            risk_score REAL,
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
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blockchain_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            function_name TEXT,
            args TEXT,
            tx_hash TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending'
        )
    ''')
    
    # Insert initial stats if not exists
    cursor.execute('''
        INSERT OR IGNORE INTO system_stats (id, total_analyzed, fake_detected, reports_sent)
        VALUES (1, 0, 0, 0)
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Train ML models
    ml_detector.train_models()
    
    # Start Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)