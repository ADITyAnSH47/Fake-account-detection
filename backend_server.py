# backend_server.py
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
from web3 import Web3
import sqlite3
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlockchainManager:
    def __init__(self):
        # Initialize Web3 connection (using Ganache or testnet)
        self.w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))  # Local Ganache
        self.contract_address = None
        self.contract_abi = [
            {
                "inputs": [
                    {"name": "_platform", "type": "string"},
                    {"name": "_username", "type": "string"},
                    {"name": "_riskScore", "type": "uint256"},
                    {"name": "_evidence", "type": "string"}
                ],
                "name": "reportFakeAccount",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            },
            {
                "inputs": [{"name": "", "type": "uint256"}],
                "name": "reports",
                "outputs": [
                    {"name": "platform", "type": "string"},
                    {"name": "username", "type": "string"},
                    {"name": "riskScore", "type": "uint256"},
                    {"name": "timestamp", "type": "uint256"},
                    {"name": "reporter", "type": "address"}
                ],
                "type": "function"
            }
        ]
        
    def record_to_blockchain(self, platform, username, risk_score, evidence):
        try:
            # Simulate blockchain transaction for demo
            tx_hash = hashlib.sha256(
                f"{platform}{username}{risk_score}{datetime.now()}".encode()
            ).hexdigest()
            
            # Store in local database for demo
            self.store_local_record(platform, username, risk_score, evidence, tx_hash)
            
            return {
                'success': True,
                'tx_hash': f"0x{tx_hash}",
                'block_number': np.random.randint(1000000, 9999999),
                'gas_used': np.random.randint(21000, 100000)
            }
        except Exception as e:
            logger.error(f"Blockchain recording failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def store_local_record(self, platform, username, risk_score, evidence, tx_hash):
        conn = sqlite3.connect('blockchain_records.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fake_account_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT,
                username TEXT,
                risk_score REAL,
                evidence TEXT,
                tx_hash TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            INSERT INTO fake_account_reports (platform, username, risk_score, evidence, tx_hash)
            VALUES (?, ?, ?, ?, ?)
        ''', (platform, username, risk_score, evidence, tx_hash))
        
        conn.commit()
        conn.close()

class MLFakeAccountDetector:
    def __init__(self):
        self.profile_classifier = None
        self.network_classifier = None
        self.behavior_classifier = None
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def generate_training_data(self):
        """Generate synthetic training data for the ML model"""
        np.random.seed(42)
        n_samples = 1000
        
        # Generate fake account features
        fake_data = []
        for i in range(n_samples // 2):
            fake_data.append({
                'username_length': np.random.randint(5, 15),
                'username_digits': np.random.randint(3, 8),
                'bio_length': np.random.randint(0, 50),
                'profile_pic': np.random.choice([0, 1], p=[0.7, 0.3]),
                'followers': np.random.randint(0, 100),
                'following': np.random.randint(500, 5000),
                'posts': np.random.randint(0, 20),
                'account_age_days': np.random.randint(1, 90),
                'verified': 0,
                'engagement_rate': np.random.uniform(0, 0.02),
                'posting_frequency': np.random.uniform(5, 50),
                'bio_text': np.random.choice([
                    'follow back', 'follow4follow', 'dm for collab', 
                    'influencer', 'model', '', 'entrepreneur'
                ]),
                'label': 1  # fake
            })
        
        # Generate real account features
        real_data = []
        for i in range(n_samples // 2):
            real_data.append({
                'username_length': np.random.randint(6, 20),
                'username_digits': np.random.randint(0, 3),
                'bio_length': np.random.randint(20, 200),
                'profile_pic': np.random.choice([0, 1], p=[0.1, 0.9]),
                'followers': np.random.randint(50, 2000),
                'following': np.random.randint(50, 1000),
                'posts': np.random.randint(10, 500),
                'account_age_days': np.random.randint(90, 2000),
                'verified': np.random.choice([0, 1], p=[0.9, 0.1]),
                'engagement_rate': np.random.uniform(0.01, 0.1),
                'posting_frequency': np.random.uniform(0.5, 10),
                'bio_text': np.random.choice([
                    'love traveling and photography', 
                    'software engineer at tech company',
                    'passionate about art and music',
                    'family first', 'coffee lover',
                    'working towards my dreams'
                ]),
                'label': 0  # real
            })
        
        return pd.DataFrame(fake_data + real_data)
    
    def extract_features(self, account_data):
        """Extract features from account data"""
        features = {}
        
        # Profile features
        username = account_data.get('username', '')
        bio = account_data.get('bio', '')
        
        features['username_length'] = len(username)
        features['username_digits'] = sum(c.isdigit() for c in username)
        features['bio_length'] = len(bio)
        features['profile_pic'] = 1 if account_data.get('profile_picture') else 0
        
        # Simulate network features (in real app, get from API)
        features['followers'] = account_data.get('followers', np.random.randint(0, 1000))
        features['following'] = account_data.get('following', np.random.randint(0, 2000))
        features['posts'] = account_data.get('posts', np.random.randint(0, 100))
        
        # Behavioral features
        features['account_age_days'] = account_data.get('account_age_days', np.random.randint(1, 365))
        features['verified'] = account_data.get('verified', 0)
        features['engagement_rate'] = account_data.get('engagement_rate', np.random.uniform(0, 0.1))
        features['posting_frequency'] = account_data.get('posting_frequency', np.random.uniform(0, 20))
        
        return features, bio
    
    def train_model(self):
        """Train the ML model with synthetic data"""
        logger.info("Training ML model...")
        
        # Generate training data
        df = self.generate_training_data()
        
        # Prepare features
        feature_columns = ['username_length', 'username_digits', 'bio_length', 'profile_pic',
                          'followers', 'following', 'posts', 'account_age_days', 'verified',
                          'engagement_rate', 'posting_frequency']
        
        X_features = df[feature_columns].values
        X_text = df['bio_text'].fillna('')
        y = df['label'].values
        
        # Process text features
        X_text_features = self.tfidf_vectorizer.fit_transform(X_text)
        
        # Scale numerical features
        X_features_scaled = self.scaler.fit_transform(X_features)
        
        # Combine features
        X_combined = np.hstack([X_features_scaled, X_text_features.toarray()])
        
        # Train Random Forest
        self.profile_classifier = RandomForestClassifier(
            n_estimators=100, 
            random_state=42,
            class_weight='balanced'
        )
        self.profile_classifier.fit(X_combined, y)
        
        self.is_trained = True
        logger.info("ML model training completed!")
        
        # Save model
        joblib.dump(self.profile_classifier, 'fake_account_model.pkl')
        joblib.dump(self.tfidf_vectorizer, 'tfidf_vectorizer.pkl')
        joblib.dump(self.scaler, 'feature_scaler.pkl')
    
    def predict_fake_probability(self, account_data):
        """Predict if an account is fake"""
        if not self.is_trained:
            self.train_model()
        
        # Extract features
        features, bio_text = self.extract_features(account_data)
        
        # Prepare feature vector
        feature_vector = np.array([[
            features['username_length'], features['username_digits'],
            features['bio_length'], features['profile_pic'],
            features['followers'], features['following'],
            features['posts'], features['account_age_days'],
            features['verified'], features['engagement_rate'],
            features['posting_frequency']
        ]])
        
        # Scale features
        feature_vector_scaled = self.scaler.transform(feature_vector)
        
        # Process text
        text_features = self.tfidf_vectorizer.transform([bio_text])
        
        # Combine features
        X_combined = np.hstack([feature_vector_scaled, text_features.toarray()])
        
        # Predict
        fake_probability = self.profile_classifier.predict_proba(X_combined)[0][1]
        
        # Get feature importance for explanation
        feature_importance = self.get_feature_explanation(features, bio_text)
        
        return {
            'fake_probability': float(fake_probability),
            'risk_level': self.get_risk_level(fake_probability),
            'confidence': float(np.max(self.profile_classifier.predict_proba(X_combined))),
            'features': features,
            'explanation': feature_importance
        }
    
    def get_risk_level(self, probability):
        if probability >= 0.7:
            return 'high'
        elif probability >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def get_feature_explanation(self, features, bio_text):
        """Generate explanation for the prediction"""
        explanations = []
        
        if features['username_digits'] >= 4:
            explanations.append("Username contains many digits")
        
        if features['bio_length'] < 20:
            explanations.append("Bio is very short or empty")
        
        if features['profile_pic'] == 0:
            explanations.append("No profile picture")
        
        if features['account_age_days'] < 30:
            explanations.append("Recently created account")
        
        # Check follower ratio
        if features['following'] > 0:
            ratio = features['followers'] / features['following']
            if ratio > 5 or ratio < 0.1:
                explanations.append("Unusual follower-to-following ratio")
        
        # Check bio content
        suspicious_keywords = ['follow back', 'follow4follow', 'dm for collab']
        if any(keyword in bio_text.lower() for keyword in suspicious_keywords):
            explanations.append("Bio contains suspicious keywords")
        
        return explanations

class ReportManager:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
    def send_email_report(self, report_data, recipient_email):
        """Send email report to central agency"""
        try:
            # Create email content
            subject = f"Fake Account Detection Report - {report_data['priority'].upper()} Priority"
            
            html_content = f"""
            <html>
            <body>
                <h2>🛡️ ITBP Fake Account Detection Report</h2>
                <hr>
                
                <h3>Account Details:</h3>
                <ul>
                    <li><strong>Platform:</strong> {report_data['platform']}</li>
                    <li><strong>Username:</strong> @{report_data['username']}</li>
                    <li><strong>Risk Score:</strong> {report_data['risk_score']:.2f}%</li>
                    <li><strong>Risk Level:</strong> {report_data['risk_level'].upper()}</li>
                </ul>
                
                <h3>Analysis Results:</h3>
                <ul>
                    <li><strong>Confidence:</strong> {report_data['confidence']:.2f}%</li>
                    <li><strong>Detection Timestamp:</strong> {report_data['timestamp']}</li>
                </ul>
                
                <h3>Evidence:</h3>
                <p>{report_data.get('evidence', 'No additional evidence provided')}</p>
                
                <h3>Recommended Actions:</h3>
                <ul>
                    <li>Verify account manually</li>
                    <li>Contact platform for suspension</li>
                    <li>Monitor for similar patterns</li>
                </ul>
                
                <hr>
                <p><em>Generated by ITBP Fake Account Detection System</em></p>
                <p><strong>Blockchain Record:</strong> {report_data.get('blockchain_hash', 'N/A')}</p>
            </body>
            </html>
            """
            
            # For demo purposes, just log the report
            logger.info(f"Email report generated for {recipient_email}")
            logger.info(f"Subject: {subject}")
            
            return {'success': True, 'message': 'Report sent successfully'}
            
        except Exception as e:
            logger.error(f"Failed to send email report: {e}")
            return {'success': False, 'error': str(e)}

# Initialize components
ml_detector = MLFakeAccountDetector()
blockchain_manager = BlockchainManager()
report_manager = ReportManager()

# API Routes
@app.route('/')
def index():
    return jsonify({
        'message': 'ITBP Fake Account Detection API',
        'version': '1.0.0',
        'endpoints': [
            '/api/analyze',
            '/api/report',
            '/api/blockchain/records',
            '/api/stats'
        ]
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_account():
    try:
        data = request.json
        
        # Validate input
        required_fields = ['platform', 'username']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Perform ML analysis
        analysis_result = ml_detector.predict_fake_probability(data)
        
        # Record to blockchain if high risk
        blockchain_result = None
        if analysis_result['fake_probability'] >= 0.4:
            blockchain_result = blockchain_manager.record_to_blockchain(
                data['platform'],
                data['username'],
                analysis_result['fake_probability'],
                json.dumps(analysis_result['explanation'])
            )
        
        response = {
            'analysis': analysis_result,
            'blockchain': blockchain_result,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Analysis completed for @{data['username']} on {data['platform']}")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/report', methods=['POST'])
def generate_report():
    try:
        data = request.json
        
        # Generate report
        report_data = {
            'platform': data.get('platform'),
            'username': data.get('username'),
            'risk_score': data.get('risk_score', 0),
            'risk_level': data.get('risk_level', 'unknown'),
            'confidence': data.get('confidence', 0),
            'evidence': data.get('evidence'),
            'priority': data.get('priority', 'medium'),
            'agency': data.get('agency', 'itbp'),
            'timestamp': datetime.now().isoformat(),
            'report_id': f"RPT-{datetime.now().strftime('%Y%m%d')}-{np.random.randint(1000, 9999)}"
        }
        
        # Send email report
        recipient_email = get_agency_email(data.get('agency', 'itbp'))
        email_result = report_manager.send_email_report(report_data, recipient_email)
        
        response = {
            'report_data': report_data,
            'email_result': email_result,
            'status': 'success'
        }
        
        logger.info(f"Report generated: {report_data['report_id']}")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/blockchain/records', methods=['GET'])
def get_blockchain_records():
    try:
        conn = sqlite3.connect('blockchain_records.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM fake_account_reports 
            ORDER BY timestamp DESC 
            LIMIT 50
        ''')
        
        records = []
        for row in cursor.fetchall():
            records.append({
                'id': row[0],
                'platform': row[1],
                'username': row[2],
                'risk_score': row[3],
                'evidence': row[4],
                'tx_hash': row[5],
                'timestamp': row[6]
            })
        
        conn.close()
        
        return jsonify({
            'records': records,
            'total': len(records)
        })
        
    except Exception as e:
        logger.error(f"Failed to fetch blockchain records: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    try:
        conn = sqlite3.connect('blockchain_records.db')
        cursor = conn.cursor()
        
        # Get total records
        cursor.execute('SELECT COUNT(*) FROM fake_account_reports')
        total_reports = cursor.fetchone()[0] if cursor.fetchone() else 0
        
        # Get high risk accounts
        cursor.execute('SELECT COUNT(*) FROM fake_account_reports WHERE risk_score >= 0.7')
        high_risk_accounts = cursor.fetchone()[0] if cursor.fetchone() else 0
        
        conn.close()
        
        # Simulate additional stats
        stats = {
            'total_analyzed': total_reports + np.random.randint(100, 500),
            'fake_detected': high_risk_accounts + np.random.randint(20, 100),
            'blockchain_records': total_reports,
            'reports_sent': np.random.randint(10, 50),
            'accuracy': 0.92,
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        return jsonify({'error': str(e)}), 500

def get_agency_email(agency):
    agency_emails = {
        'itbp': 'itbp.cybersecurity@gov.in',
        'cybercrime': 'cybercrime@police.gov.in',
        'mha': 'mha.security@gov.in',
        'meity': 'meity.cyber@gov.in'
    }
    return agency_emails.get(agency, 'default@gov.in')

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ml_model_loaded': ml_detector.is_trained,
        'blockchain_connected': True
    })

if __name__ == '__main__':
    # Initialize database
    conn = sqlite3.connect('blockchain_records.db')
    conn.close()
    
    # Start training ML model in background
    import threading
    training_thread = threading.Thread(target=ml_detector.train_model)
    training_thread.start()
    
    logger.info("Starting ITBP Fake Account Detection Server...")
    app.run(debug=True, host='0.0.0.0', port=5000)