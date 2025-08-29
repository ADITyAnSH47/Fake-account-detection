Fake Account Detection with Blockchain Integration

This project implements a Fake Account Detection System that combines Machine Learning for classification and Blockchain (Solidity Smart Contracts) for secure and transparent record-keeping.

It includes a backend server, ML model deployment setup, and blockchain smart contracts for decentralized trust management.

video link- https://drive.google.com/file/d/1YwWp_kgcFBwmqjo2P2EQ6sWDeipjfFje/view?usp=drivesdk
---

📂 Project Structure

.
├── .env                     # Environment variables (API keys, DB credentials, etc.)
├── backend_server/          # Backend server code (API, model integration)
├── blockchain_records/      # Blockchain-related data and logs
├── config/                  # Configuration files
├── deploy_contract/         # Scripts for deploying Solidity contracts
├── deployment_setup/        # Python scripts for setting up deployment
├── fake_account_model.pkl   # Trained ML model for fake account detection
├── FakeAccountRegistry.clar  # clarity Smart Contract for fake account registry
├── feature_scaler.pkl       # Scaler used for preprocessing features
├── index.html               # Frontend entry point (UI for interaction)
├── tfidf_vectorizer.pkl     # TF-IDF vectorizer used for text-based features


---

🚀 Features

Fake Account Detection (ML Model)

Trained model (fake_account_model.pkl) with feature scaling and TF-IDF vectorization.


Blockchain Integration

Smart contract FakeAccountRegistry.clar ensures tamper-proof logging of detection results.


Deployment Ready

Backend APIs and deployment setup scripts provided.


Scalable Architecture

Modular code structure for easy updates and improvements.




---

⚙ Installation

1. Clone the Repository

git clone <your-repo-url>
cd <repo-name>


2. Create Virtual Environment & Install Dependencies

python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)

pip install -r requirements.txt


3. Set Up Environment Variables

Create a .env file with necessary keys (API keys, blockchain config, etc.).





---

▶ Usage

1. Run Backend Server

python backend_server/app.py


2. Deploy Smart Contract

Use scripts inside deploy_contract/ or deploy FakeAccountRegistry.sol manually using Remix / Truffle / Hardhat.



3. Open Frontend

Launch index.html in browser to interact with the system.





---

🔄 Workflow

Here’s how the system works step by step:

flowchart TD
    A[User Input via Frontend] --> B[Preprocessing]
    B --> C[TF-IDF Vectorizer + Feature Scaler]
    C --> D[ML Model: fake_account_model.pkl]
    D -->|Prediction: Fake/Legit| E[Backend Server Response]
    D --> F[Record Result on Blockchain]
    F --> G[FakeAccountRegistry.clar]
    G --> H[Immutable Storage of Results]
    E --> I[User Sees Result + Blockchain TxID]


---

🧠 Machine Learning Details

Vectorizer: TF-IDF (tfidf_vectorizer.pkl)

Scaler: Standard Scaler (feature_scaler.pkl)

Model: Supervised ML model (fake_account_model.pkl)



---

🔗 Blockchain Details

Smart Contract: FakeAccountRegistry.clar

Functionality: Records detection results, ensures transparency and immutability.



---

📌 Future Improvements

Enhance ML model accuracy with larger datasets.

Integrate advanced NLP embeddings (e.g., BERT).

Expand blockchain functionality for decentralized verification.

Build a complete frontend with React/Next.js.



---

👨‍💻 Contributors

Adityansh 

Shreejit hait

Tosham behera
