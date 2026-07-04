# Code Cortex 🧠⚖️

> An AI-powered legal contract analysis platform — built at the Saudi Digital Academy Hackathon

---

## Overview

Code Cortex simplifies reading complex Arabic contracts. Upload your contract and instantly get a plain-language breakdown, risk analysis, and direct answers to your questions — powered by Anthropic's Claude and a RAG engine trained on Saudi law.

---

## Features

| Feature | Description |
|---------|-------------|
| 🔐 Authentication & RBAC | Secure user and lawyer accounts with role-based access control |
| 📄 AI Contract Analysis | Upload a contract and get instant risk analysis powered by Claude AI |
| 💬 RAG-based Q&A | Ask direct questions about your contract using the built-in RAG engine |
| 🏛️ Saudi Law Reference | Legal context retrieved from Saudi regulations via ChromaDB |
| 👨‍⚖️ Lawyer Directory | Browse certified lawyers and contact them directly |
| 🌐 Community Page | Share contract experiences and advice (registered users only) |
| 📱 Modern UI | Responsive design built with React and Vite |

---

## Tech Stack

### Frontend
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![React Router](https://img.shields.io/badge/React_Router-CA4245?style=for-the-badge&logo=react-router&logoColor=white)

### Backend
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens)

### AI & Search
![Claude](https://img.shields.io/badge/Claude_AI-D97757?style=for-the-badge&logo=anthropic&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6B35?style=for-the-badge)

---

## Project Structure

```
ContractScan-AI/
├── backend/
│   ├── main.py              # FastAPI app + AI endpoints
│   ├── rag_engine.py        # RAG system for Saudi law
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # SQLite connection
│   ├── security.py          # JWT authentication
│   ├── routes/
│   │   ├── auth.py
│   │   ├── users.py
│   │   └── admin.py
│   └── data/                # Saudi law dataset
└── frontend/
    └── src/
        ├── pages/
        │   ├── ContractPage.jsx
        │   ├── AnalyzePage.jsx
        │   ├── RsultPage.jsx
        │   ├── LawyersPage.jsx
        │   ├── CommunityPage.jsx
        │   ├── Dashboard.jsx
        │   └── Admin.jsx
        └── components/
            ├── Navbar.jsx
            └── ProtectedRoute.jsx
```

---

## Getting Started

### Requirements

- Python 3.10+
- Node.js 18+
- Anthropic API Key

### 1. Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Run the server
uvicorn main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`

### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

App runs at `http://localhost:5173`

---

## Team

Built at the **Saudi Digital Academy Hackathon**

  Team :
| Saja Alkhalaf 
| Ramah Alharbi
| Sarah Alowjan
| Farah Alshibani

---

## License

MIT License — Academic project built for learning purposes
