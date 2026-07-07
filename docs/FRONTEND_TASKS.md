# Frontend Development Guide & Tasks

This document outlines the architecture of the frontend for the AMD Zero-Token Router and details the pending tasks required to finalize the integration.

## Current Architecture

Our frontend is a modern Next.js 14+ application using the App Router, heavily utilizing Tailwind CSS and Framer Motion to achieve an "Award-Winning / Dribbble" premium aesthetic. 

1.  **Landing Page (`src/app/page.tsx`)**: A highly interactive, dark-mode, glassmorphic landing page. Features scroll-based parallax, a custom cursor (`CustomCursor.tsx`), and magnetic physics buttons (`MagneticButton.tsx`).
2.  **Chat Dashboard (`src/app/chat/page.tsx`)**: A premium IDE-style console. It features a sidebar, an analytics panel to show live metrics (Tokens Saved, Topology active layer, Active Instance), and the main chat UI.
3.  **Iconography**: We use a mix of `lucide-react` for standard UI elements and `reicon-react` for high-end, detailed icons (like `Cpu3`).

## Pending Tasks for Frontend Developer

### 1. Wire Up the Chat API
The chat interface currently uses hardcoded UI elements and dummy data. You need to connect it to the FastAPI backend.
*   **Action**: In `src/app/chat/page.tsx`, implement a fetch call inside the `handleInput` or a submit function.
*   **Endpoint**: `POST http://localhost:8000/api/route`
*   **Payload**: `{ "prompt": input }`

### 2. Dynamic UI Updates Based on Response
When the backend responds, it will return the generated text, the `model_selected`, the `tokens_saved`, and the `routing_layer`.
*   **Action**: Update the React state to append the user's message and the AI's response to the chat feed.
*   **Action**: Update the Analytics Sidebar dynamically:
    *   Change the **Active Instance** text to match `model_selected` (e.g., Llama 3 8B or 70B).
    *   Increment the **Tokens Saved** metric by the `tokens_saved` value returned from the API.
    *   Highlight the active layer in the **Routing Topology** based on the `routing_layer` variable (`semantic`, `xgboost`, or `fallback`).

### 3. Add Loading States
Currently, there is no loading indicator when a message is sent.
*   **Action**: Disable the input field or show a glowing pulse effect on the send button while waiting for the FastAPI backend to respond.

### How to Run Locally
```bash
cd frontend
npm install
npm run dev
```
Access the app at `http://localhost:3000`.
