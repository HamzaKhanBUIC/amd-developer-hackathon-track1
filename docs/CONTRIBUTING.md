# Contributor Guidelines & Workflow

Welcome team! Let's build something astonishing.

## Execution Sequence (Who Works When)

To avoid merge conflicts and blocked tasks, we will execute in three parallel but staggered phases:

### Phase 1: Foundation (Hours 1 - 12)
- **Member 2 (Lead) & AI:** Set up GitHub repository, define architecture (PROJECT_DNA), and scaffold `/frontend` and `/backend` with Docker.
- **Member 3 (Backend):** Begin drafting the FastAPI endpoints and generating the initial mock datasets in `/backend`.
- **Member 1 (Frontend):** Start building the core layout shell in Next.js using our Stitch-inspired dark mode aesthetic.

### Phase 2: Integration & Logic (Hours 12 - 48)
- **Member 3 & Lead:** Train the XGBoost classifier and integrate the Semantic Router. Connect FastAPI to the Fireworks API.
- **Member 1 (Frontend):** Connect the UI to the backend `/api/route` endpoints. Ensure micro-animations are responsive and fluid.
- **Member 4 (Presentation & UI Support):** Draft the presentation script, prepare video recording software (OBS, Remotion, etc.), and assist Member 1 with minor UI tweaks and debugging.

### Phase 3: Polish & Submission (Hours 48 - 72)
- **Member 4:** Record the final demo video and finalize the pitch deck.
- **Lead & AI:** Perform final rigorous code reviews, load testing, and token optimization verification. 
- **All:** Final merge to `main` and deploy.

## Pull Request & Code Review Protocol

**Do NOT merge your own PRs.**
- The **Lead (Hamza) and AI (Antigravity)** will be acting as the central gatekeepers for the `main` branch.
- When you submit a PR, we will use our automated and manual review skills (such as `code-reviewer`, `vibe-code-auditor`, and `git-pr-review`) to verify:
  1. No "AI Slop" or generic code was introduced.
  2. The code adheres strictly to the `PROJECT_DNA.md` spec.
  3. No architectural regressions occur.

Once approved, the Lead will merge the PR. Please see the `docs/team/` folder for your specific personal guidelines and tasks.
