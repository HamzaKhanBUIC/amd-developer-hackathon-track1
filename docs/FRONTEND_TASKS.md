# Frontend Development Guide & Tasks

This document is the **master guide for the frontend developer**. It explains the current state of the repository, the architecture, and the precise, step-by-step tasks you need to complete to finish the AMD Zero-Token Router integration.

---

## 🏗️ 1. Current State & Architecture

The frontend is a modern **Next.js 14+ (App Router)** application. It is built using **Tailwind CSS**, **Framer Motion**, and premium icons from `lucide-react` and `reicon-react`.

### Important Files
1.  **`src/app/page.tsx` (Landing Page)**: A highly interactive, dark-mode, glassmorphic landing page. It uses a custom physics-based cursor and magnetic buttons. **(NO FURTHER WORK REQUIRED HERE)**.
2.  **`src/app/chat/page.tsx` (Chat Dashboard)**: The premium IDE-style chat console. This is the core application where users submit queries to the backend. **(THIS IS WHERE YOU WILL WORK)**.
3.  **`src/components/ui/`**: Contains reusable, highly-animated components like `MagneticButton.tsx` and `CustomCursor.tsx`.

---

## 🚀 2. Your Tasks

> [!IMPORTANT]
> **PIVOT: THE FRONTEND IS FOR THE PITCH VIDEO ONLY.**
> The event organizers announced that the final grading harness is a headless batch script. **The judges' automated system will never see the frontend.** 
> However, we are submitting a Pitch Video to win the aesthetic and design points. Your primary goal is to **make the Chat Dashboard look absolutely astonishing**. Connect it to the local FastAPI backend so we can record a live, flawless demo.

### Task A: State Management
Open `src/app/chat/page.tsx`. You need to manage the chat history and the live metrics.
1. Add a state array for `messages`: `const [messages, setMessages] = useState([{ role: "ai", content: "..." }])`
2. Add state variables for the analytics panel:
   * `tokensSaved` (number, default: 0)
   * `activeInstance` (string, default: "Waiting...")
   * `activeLayer` (string, default: "None")

### Task B: Wire Up the API Call
Inside `src/app/chat/page.tsx`, locate the `handleInput` or create a new `handleSubmit` function that triggers when the user clicks the "Send" button or presses `Enter`.

1. Read the value of the `textarea` input.
2. Immediately append the user's message to the `messages` state so it appears in the UI instantly.
3. Clear the `textarea`.
4. Make a `POST` request to the backend:
   ```javascript
   const response = await fetch("http://localhost:8000/api/route", {
     method: "POST",
     headers: { "Content-Type": "application/json" },
     body: JSON.stringify({ prompt: input })
   });
   const data = await response.json();
   ```

### Task C: Handle the Response & Update UI
Once you receive the `data` from the API, you must parse it and update the UI:
1. **Append the AI Message**: The API returns `data.response`. Append this to your `messages` array so the user sees the answer.
2. **Update Tokens Saved**: The API returns `data.tokens_saved`. Add this to your `tokensSaved` state. Update the Metric Card on the left sidebar to show this live number instead of the hardcoded "1.2M".
3. **Update Active Instance**: The API returns `data.model_selected` (e.g., `accounts/fireworks/models/gemma-4-26b-a4b-it` or `kimi-k2p7-code`). Display a clean version of this string in the "Active Instance" panel.
4. **Update Topology Visualization**: The API returns `data.routing_layer` (`semantic`, `xgboost-easy`, `xgboost-reasoning`, `xgboost-code` or `fallback`). 
   * If `semantic`, highlight the `L1 Semantic Filter` node.
   * If `xgboost`, highlight the `L2 Zero-Token Router` node.
   * If `fallback`, highlight the `L3 Cloud Fallback` node.

### Task D: Implement Loading States
* While the `fetch` request is pending, disable the `textarea` and the send button to prevent spam.
* Consider adding a small "typing indicator" or a glowing pulse effect to the send button so the user knows the AI is processing the request.

---

## 🛠️ 3. How to Run & Test

1. Ensure your backend teammate has the FastAPI server running on port `8000`.
2. Open a terminal in the `/frontend` folder.
3. Run `npm install` (if you haven't already).
4. Run `npm run dev`.
5. Navigate to `http://localhost:3000/chat`.
6. Open your browser's Developer Tools (Network tab) to ensure the CORS requests to `localhost:8000` are succeeding.
