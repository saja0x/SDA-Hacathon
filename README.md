Code Cortex 🧠⚖️
Code Cortex is an AI-powered legal contract analysis platform utilizing Anthropic's Claude and RAG (Retrieval-Augmented Generation). The project aims to simplify reading complex contracts, extracting key clauses, and analyzing potential legal risks.

✨ Key Features
🔐 Authentication & RBAC: Secure user and lawyer accounts with role-based access control.
📄 AI Contract Analysis: Upload a contract and ask direct questions using the built-in RAG engine.
💬 Interactive Community: A dedicated space to share contract experiences and advice (available for registered users).
👨‍⚖️ Lawyer Directory: Browse certified lawyers and contact them directly via WhatsApp.
📱 Modern UI: Responsive design and intuitive user experience built with the latest web technologies.
🛠️ Tech Stack
Frontend: React.js + Vite + React Router
Backend: FastAPI + SQLite (SQLAlchemy) + JWT Authentication
AI Integration: Anthropic Claude API + RAG Engine (Sentence Transformers & ChromaDB)
🚀 How to Run (Local Development)
1. Backend Setup
Open a terminal and navigate to the backend directory:

cd Hacathon/backend

# Activate the virtual environment (if available)
.venv\Scripts\activate.bat

# Install required packages
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --port 8000
The backend will be available at: http://localhost:8000

2. Frontend Setup
Open a new terminal and navigate to the frontend directory:

cd Hacathon/frontend

# Install dependencies
npm install

# Start the development server
npm run dev
The application will be available at: http://localhost:5173

📂 Project Structure
Hacathon/backend/: Contains the FastAPI application, SQLite database (app.db), and the AI engine (rag_engine.py).
Hacathon/frontend/: Contains the React UI, components, routing, and styles.
