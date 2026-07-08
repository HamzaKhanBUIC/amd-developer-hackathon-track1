# Hackathon Track 1 Constraints & Scope

> [!CAUTION]
> **TEAM MANDATE:** Do not deviate from these constraints. Any models used outside of this list will result in immediate disqualification from Track 1.

## 1. Allowed Models
We are strictly limited to the following Fireworks AI models:
- `minimax-m3`
- `kimi-k2p7-code`
- `gemma-4-31b-it`
- `gemma-4-26b-a4b-it`
- `gemma-4-31b-it-nvfp4`

## 2. Required Categories
The routing agent must be capable of handling queries across exactly 8 categories:
1. Factual Q&A
2. Math Reasoning
3. Sentiment Analysis
4. Summarization
5. NER (Named Entity Recognition)
6. Code Debugging
7. Logic Puzzles
8. Code Generation

## 3. Evaluation Criteria (How to Impress the Judges)
- **Accuracy Gate:** The output must actually be correct. If the routing chooses a cheap model that hallucinates, we fail.
- **Token Efficiency:** If we pass the accuracy gate, we are ranked strictly by how many tokens we saved.
- **Our Advantage:** Our Zero-Token Router uses an ultra-fast XGBoost model and AMD ROCm PyTorch embeddings to determine query complexity *locally* in 50ms, meaning our routing overhead costs exactly 0 LLM tokens, instantly giving us a massive competitive edge on the token efficiency leaderboard.

## 4. Submission Format
- Must be a self-contained `Docker` image.
