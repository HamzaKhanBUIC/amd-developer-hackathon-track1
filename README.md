# AMD Hackathon Track 1: Hybrid Token-Efficient Routing Agent

Welcome to our project repository for the AMD Developer Hackathon: ACT II (Track 1). 

Our goal is to build an AI agent that dynamically routes incoming queries to the most cost-efficient Fireworks AI model (e.g., Llama 3 8B vs 70B) while maintaining absolute accuracy, spending exactly 0 LLM tokens on the routing overhead itself.

---

## 👥 Team Onboarding & Tasks

To make collaboration seamless, the project is split into distinct frontend and backend environments. **Please read the guide specific to your role before you start coding!**

### 🎨 Frontend Team
We are building a highly interactive, dashboard using Next.js, Framer Motion, and Tailwind CSS.
👉 **[Read the Frontend Guide & Tasks](./docs/FRONTEND_TASKS.md)**

### ⚙️ Backend Team
We are building a Zero-Token Semantic Pipeline using Python, FastAPI, XGBoost, and SentenceTransformers to run local classification before hitting the cloud.
👉 **[Read the Backend Guide & Tasks](./docs/BACKEND_TASKS.md)**

---

## 📁 Project Structure
- `/frontend`: Next.js UI (React 18, Tailwind CSS, Framer Motion)
- `/backend`: FastAPI Python server containing the Zero-Token Semantic Pipeline.
- `/docs`: Technical architecture, contributor guidelines, and task lists.

## 🚀 Quick Start (Full Stack)
If you want to run both environments locally to test the full integration:

**1. Start the Backend**
```bash
cd backend
pip install -r requirements.txt
python train_model.py
uvicorn main:app --reload --port 8000
```

**2. Start the Frontend**
```bash
cd frontend
npm install
npm run dev
```
The app will be available at `http://localhost:3000`.
