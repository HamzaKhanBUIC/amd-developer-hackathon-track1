# AMD Hackathon Track 1: Hybrid Token-Efficient Routing Agent

Welcome to our project repository for the AMD Developer Hackathon: ACT II (Track 1). 

Our goal is to build an AI agent that dynamically routes incoming queries to the most cost-efficient Fireworks AI allowed model (`gemma-4-26b-a4b-it` vs `kimi-k2p7-code` vs `gemma-4-31b-it`) while maintaining absolute accuracy across 8 specific categories, spending exactly 0 LLM tokens on the routing overhead itself.

👉 **[Read the Mandatory Track 1 Requirements](./docs/TRACK_1_REQUIREMENTS.md)**

---

## 👥 Team Onboarding & Tasks

To make collaboration seamless, the project is split into distinct frontend and backend environments. **Please read the guide specific to your role before you start coding!**

### 🎨 Frontend Team
We are building a highly interactive, dashboard using Next.js, Framer Motion, and Tailwind CSS.
👉 **[Read the Frontend Guide & Tasks](./docs/FRONTEND_TASKS.md)**

### 💎 Design System
We adhere strictly to a premium, glassmorphic dark mode aesthetic. All components, layouts, and typography must follow the established system.
👉 **[Read the Aesthetic Design Rules](./docs/DESIGN.md)**

### ⚙️ Backend Team
We are building a Zero-Token Semantic Pipeline using Python, FastAPI, XGBoost, and SentenceTransformers to run local classification before hitting the cloud. The pipeline has been updated to use unified dense vectors (dropping TF-IDF) and explicitly targets **AMD ROCm/CUDA acceleration** for embedding throughput.
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
python generate_dataset.py
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

---

## 🐳 Docker (Hackathon Submission Format)
To run the entire full-stack application as a single Docker container (as required by the Track 1 submission rules):
```bash
docker build -t amd-track1-agent .
docker run -p 3000:3000 -p 8000:8000 -e FIREWORKS_API_KEY="your_key" amd-track1-agent
```
